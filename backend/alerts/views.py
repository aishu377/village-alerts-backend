import math
import requests
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Alert, UserDevice
from .serializers import AlertSerializer, UserDeviceSerializer


def haversine_distance(lat1, lon1, lat2, lon2):
    """Returns distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class AlertListView(APIView):
    """
    GET /api/alerts/?lat=12.97&lon=77.59&categories=weather,pest
    Returns alerts relevant to the user's location and subscribed categories.
    Filters by: active, not expired, within radius.
    """

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        categories = request.query_params.get('categories', '')
        district = request.query_params.get('district', '')

        qs = Alert.objects.filter(is_active=True)

        # Filter by expiry
        now = timezone.now()
        qs = qs.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        )

        # Filter by categories if provided
        if categories:
            cat_list = [c.strip() for c in categories.split(',')]
            qs = qs.filter(category__in=cat_list)

        # Filter by district if no GPS
        if district and not (lat and lon):
            qs = qs.filter(district__iexact=district)

        alerts = list(qs)

        # If GPS available, filter by radius
        if lat and lon:
            try:
                lat, lon = float(lat), float(lon)
                alerts = [
                    a for a in alerts
                    if (
                        a.latitude is None or a.longitude is None or
                        haversine_distance(lat, lon, a.latitude, a.longitude) <= a.radius_km
                    )
                ]
            except ValueError:
                pass

        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)


class AlertDetailView(APIView):
    """GET /api/alerts/<id>/"""

    def get(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk, is_active=True)
        except Alert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AlertSerializer(alert).data)


class RegisterDeviceView(APIView):
    """
    POST /api/devices/register/
    Body: { fcm_token, village, district, state, latitude, longitude, subscribed_categories }
    Registers or updates a device for push notifications.
    """

    def post(self, request):
        token = request.data.get('fcm_token')
        if not token:
            return Response({'error': 'fcm_token required'}, status=status.HTTP_400_BAD_REQUEST)

        device, created = UserDevice.objects.update_or_create(
            fcm_token=token,
            defaults={
                'village': request.data.get('village', ''),
                'district': request.data.get('district', ''),
                'state': request.data.get('state', ''),
                'latitude': request.data.get('latitude'),
                'longitude': request.data.get('longitude'),
                'subscribed_categories': request.data.get(
                    'subscribed_categories',
                    ['weather', 'pest', 'water', 'market', 'scheme', 'community', 'emergency']
                ),
            }
        )
        return Response(
            UserDeviceSerializer(device).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class WeatherAlertView(APIView):
    """
    GET /api/weather/?lat=12.97&lon=77.59
    Fetches live weather from OpenWeatherMap and returns a structured alert-style response.
    Free API — no IMD key needed for MVP.
    """

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')

        if not lat or not lon:
            return Response({'error': 'lat and lon required'}, status=400)

        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return Response({'error': 'Weather API key not configured'}, status=503)

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        )
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
        except Exception as e:
            return Response({'error': str(e)}, status=503)

        weather_main = data.get('weather', [{}])[0]
        main = data.get('main', {})
        wind = data.get('wind', {})

        # Determine severity
        condition_id = weather_main.get('id', 800)
        if condition_id < 300:
            severity = 'red'   # Thunderstorm
        elif condition_id < 600:
            severity = 'yellow'  # Rain
        else:
            severity = 'green'

        return Response({
            'condition': weather_main.get('description', 'Clear').title(),
            'temperature_c': main.get('temp'),
            'humidity_pct': main.get('humidity'),
            'wind_kmh': round(wind.get('speed', 0) * 3.6, 1),
            'severity': severity,
            'city': data.get('name', ''),
            'icon_code': weather_main.get('icon', '01d'),
        })


class HealthView(APIView):
    """GET /api/health/ — basic liveness check"""

    def get(self, request):
        return Response({'status': 'ok', 'service': 'village-alerts-api'})
