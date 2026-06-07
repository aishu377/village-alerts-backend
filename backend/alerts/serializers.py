from rest_framework import serializers
from .models import Alert, UserDevice


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message', 'category', 'severity',
            'village', 'district', 'state',
            'latitude', 'longitude',
            'action_label', 'action_url',
            'created_at', 'expires_at',
        ]


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = [
            'id', 'fcm_token', 'village', 'district', 'state',
            'latitude', 'longitude', 'subscribed_categories',
        ]
