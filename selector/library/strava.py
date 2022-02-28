import os
import time
from collections import Counter
from datetime import datetime
from typing import List, Optional

import requests
from django.db.models import Count

from selector.models import Activity, Auth, Gear, Segment, User

STRAVA_OAUTH_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"
ACCESS_TOKEN_FILE = ".token.json"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
AUTHORIZATION_CODE = os.environ.get("AUTHORIZATION_CODE")
ALLOWED_TYPES = {"Ride"}


def check_access_token(athlete_id: str) -> Optional[str]:
    # TODO: figure out what we want to do in a non-happy path case
    # TODO: make sure there are no opportunities for SQL injection

    athlete_auth = Auth.objects.filter(user__user_id=athlete_id)

    if not athlete_auth:
        return None

    athlete_auth = athlete_auth[0]

    expires_at = athlete_auth.expires_at
    if expires_at:
        expires_at = int(expires_at)

    if expires_at and time.time() < expires_at:
        return athlete_auth.access_token

    refresh_token = athlete_auth.refresh_token

    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(STRAVA_OAUTH_URL, params=params)
    if response.status_code != 200:
        raise Exception

    json_response = response.json()
    athlete_auth.access_token = json_response["access_token"]
    athlete_auth.refresh_token = json_response["refresh_token"]
    athlete_auth.expires_at = json_response["expires_at"]
    athlete_auth.save()
    return athlete_auth.access_token


def save_refresh_token(code: str) -> None:
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
    }
    response = requests.post(STRAVA_OAUTH_URL, params=params)
    if response.status_code != 200:
        raise Exception
    json_response = response.json()
    athlete = json_response["athlete"]
    athlete_id = athlete["id"]
    user = User(user_id=athlete_id)
    user.save()
    athlete_auth = Auth(user=user)
    athlete_auth.access_token = json_response["access_token"]
    athlete_auth.refresh_token = json_response["refresh_token"]
    athlete_auth.expires_at = json_response["expires_at"]
    athlete_auth.save()


def get_activities(athlete_id: str, page: int = 1, per_page: int = 200) -> List[dict]:
    access_token = check_access_token(athlete_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": per_page, "page": page}
    response = requests.get(
        f"{STRAVA_API_URL}/athlete/activities", headers=headers, params=params
    )
    return response.json()


def get_activity(activity_id: str, user: User) -> dict:
    access_token = check_access_token(user.user_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{STRAVA_API_URL}/activities/{activity_id}", headers=headers
    )
    return response.json()


def process_segments(segment_efforts: List[dict], activity: Activity) -> None:
    segment_objs = []
    for segment_effort in segment_efforts:
        segment = segment_effort["segment"]
        segment_id = segment["id"]
        segment_obj = Segment(segment_id=segment_id, activity=activity)
        segment_objs.append(segment_obj)

    Segment.objects.bulk_create(segment_objs)


def process_activities(user: User):
    activities = get_activities(user.user_id)
    for activity in activities:
        activity_id = activity["id"]
        type = activity["type"]
        if type not in ALLOWED_TYPES:
            continue
        full_activity = get_activity(activity_id, user)
        gear_id = full_activity["gear"]["id"]
        gear_name = full_activity["gear"]["name"]
        gear_obj, is_gear_created = Gear.objects.get_or_create(
            gear_id=gear_id, user=user, name=gear_name
        )
        if is_gear_created:
            gear_obj.save()
        activity_date_str = full_activity["start_date"].replace("Z", "+00:00")
        activity_date = datetime.fromisoformat(activity_date_str)
        activity_obj = Activity(
            activity_id=activity_id,
            user=user,
            activity_date=activity_date,
            gear=gear_obj,
        )
        activity_obj.save()
        process_segments(full_activity["segment_efforts"], activity_obj)
        time.sleep(20)


def calculate_ride_scores(segment_efforts: List[dict], user: User) -> Optional[Gear]:
    gear_id_counts = Counter()
    for segment_effort in segment_efforts:
        segment = segment_effort["segment"]
        segment_id = segment["id"]
        gear_counts = (
            Segment.objects.filter(segment_id=segment_id, activity__user=user)
            .all()
            .values("activity__gear")
            .annotate(total=Count("activity__gear"))
        )
        for gear_count in gear_counts:
            gear_id = gear_count["activity__gear"]
            count = gear_count["total"]
            gear_id_counts[gear_id] += count
    most_common_gear_id, count = gear_id_counts.most_common(1)[0]
    return Gear.objects.get(id=most_common_gear_id)


def update_gear_for_id(activity_id: str, user: User, gear: Gear) -> dict:
    access_token = check_access_token(user.user_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    description = f"👏 Gear automatically updated to {gear.name} by gear.blake.bike"
    gear_id = gear.gear_id
    response = requests.put(
        f"{STRAVA_API_URL}/activities/{activity_id}",
        headers=headers,
        json={"gear_id": gear_id, "description": description},
    )
    return response.json()


def process_new_activity(activity_id: str, owner_id: str) -> bool:
    user = User.objects.get(user_id=owner_id)
    full_activity = get_activity(activity_id, user)
    segment_efforts = full_activity["segment_efforts"]
    predicted_gear = calculate_ride_scores(segment_efforts, user)
    response = update_gear_for_id(activity_id, user, predicted_gear)
    print(response)
    # TODO: update activity with new gear
    # TODO: update activity description with credit
