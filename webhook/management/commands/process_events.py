from django.core.management.base import BaseCommand

from selector.library.strava import process_new_activity
from webhook.models import Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        non_processed_events = Event.objects.filter(is_processed=False).all()
        for event in non_processed_events:
            if event.object_type != "activity" or event.aspect_type != "create":
                print("This is not the right activity or aspect type")
                continue
            process_new_activity(event.object_id, event.owner_id)
            event.is_processed = True
            event.save()
