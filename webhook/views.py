import os

from django.http.response import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from webhook.models import Event, Subscription


@api_view(["POST", "GET"])
def webhook(request):
    # TODO: check that the code matches the one we would have sent
    # TODO: analyze the segments
    # TODO: update the activity with the results
    if request.method == "GET":
        return process_initial_webhook_request(request)
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


def process_initial_webhook_request(request):

    hub_mode = request.GET.get("hub.mode")
    hub_challenge = request.GET.get("hub.challenge")
    hub_verify_token = request.GET.get("hub.verify_token")

    # check if the hub.verify_token is what we were expecting
    if os.environ.get("VERIFY_TOKEN") != hub_verify_token:
        return HttpResponse("Unauthorized", status=401)

    subscription = Subscription(
        mode=hub_mode, challenge=hub_challenge, verify_token=hub_verify_token
    )
    subscription.save()

    return JsonResponse({"hub.challenge": hub_challenge})
