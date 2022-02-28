from django.core.management.base import BaseCommand

from selector.library.strava import process_activities
from selector.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        non_backfilled_users = User.objects.filter(backfilled=False)
        for user in non_backfilled_users:
            process_activities(user)
