from django.db import models


class Alert(models.Model):
    CATEGORY_CHOICES = [
        ('weather', 'Weather'),
        ('pest', 'Pest & Disease'),
        ('water', 'Water Availability'),
        ('market', 'Market'),
        ('scheme', 'Government Scheme'),
        ('community', 'Community'),
        ('emergency', 'Emergency'),
    ]

    SEVERITY_CHOICES = [
        ('green', 'Advisory'),
        ('yellow', 'Warning'),
        ('red', 'Critical'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='green')

    # Location fields
    village = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    radius_km = models.FloatField(default=30.0)

    action_label = models.CharField(max_length=100, blank=True)
    action_url = models.CharField(max_length=300, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_severity_display().upper()}][{self.category.upper()}] {self.title}"


class UserDevice(models.Model):
    """Stores device FCM tokens for push notifications."""
    fcm_token = models.CharField(max_length=500, unique=True)
    village = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    subscribed_categories = models.JSONField(
        default=list,
        help_text="List of alert category keys the user subscribed to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.village or self.district} — {self.fcm_token[:20]}..."
