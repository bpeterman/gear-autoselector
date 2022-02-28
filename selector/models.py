from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=200, unique=True)
    backfilled = models.BooleanField(default=False)


class Gear(models.Model):
    gear_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Activity(models.Model):
    activity_id = models.CharField(max_length=200, unique=True)
    activity_date = models.DateTimeField("activity date")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear = models.ForeignKey(Gear, on_delete=models.CASCADE)


class Auth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    expires_at = models.IntegerField()


class Segment(models.Model):
    segment_id = models.CharField(max_length=200)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
