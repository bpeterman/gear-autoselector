from django.db import models


class Event(models.Model):
    aspect_type = models.CharField(max_length=50)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=200)
    owner_id = models.CharField(max_length=200)
    subscription_id = models.CharField(max_length=200)
    event_time = models.IntegerField()
    updates = models.JSONField()
    is_processed = models.BooleanField(default=False)


class Subscription(models.Model):
    mode = models.CharField(max_length=50)
    challenge = models.CharField(max_length=200)
    verify_token = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
