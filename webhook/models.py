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
