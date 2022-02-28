from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from webhook.models import Event


@api_view(["POST"])
def webhook(request):
    # TODO: check that the code matches the one we would have sent
    # TODO: analyze the segments
    # TODO: update the activity with the results
    request_data = JSONParser().parse(request)
    aspect_type = request_data["aspect_type"]
    object_type = request_data["object_type"]
    object_id = request_data["object_id"]
    owner_id = request_data["owner_id"]
    subscription_id = request_data["subscription_id"]
    event_time = request_data["event_time"]
    updates = request_data["updates"]

    event = Event(
        aspect_type=aspect_type,
        object_type=object_type,
        object_id=object_id,
        owner_id=owner_id,
        subscription_id=subscription_id,
        event_time=event_time,
        updates=updates,
    )
    event.save()

    return JsonResponse({"success": True})
