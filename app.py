import json
import os
import time
from collections import Counter
from typing import List, Optional

import requests

STRAVA_OAUTH_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"
ACCESS_TOKEN_FILE = ".token.json"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
AUTHORIZATION_CODE = os.environ.get("AUTHORIZATION_CODE")
FRAME_TYPE_MAPPING = {1: "mountain", 2: "gravel", 3: "road"}
SEGMENTS = {}
ACTIVITIES = {}
BIKE_MAPPING = {
    "b6041696": {"name": "tarmac", "frame_type": 3},
    "b5876566": {"name": "tallboy", "frame_type": 1},
    "b7660312": {"name": "warbird", "frame_type": 2},
}
FRAME_TYPE_TO_ID = {"3": "b6041696", "1": "b5876566", "2": "b7660312"}


def check_access_token() -> str:
    data = {}
    with open(ACCESS_TOKEN_FILE) as access_token_file:
        data = json.load(access_token_file)

    expires_at = data.get("expires_at")
    if expires_at:
        expires_at = int(expires_at)

    if expires_at and time.time() < expires_at:
        current_access_token = data.get("access_token")
        return current_access_token

    refresh_token = data.get("refresh_token")
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(STRAVA_OAUTH_URL, params=params)
    if response.status_code != 200:
        raise Exception
    with open(ACCESS_TOKEN_FILE, "w") as access_token_file:
        json.dump(response.json(), access_token_file, indent=4, sort_keys=True)
    return response.json()["access_token"]


def get_activities() -> List[dict]:
    access_token = check_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{STRAVA_API_URL}/athlete/activities", headers=headers)
    print(response.json())


def get_activity(activity_id: str) -> dict:
    access_token = check_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{STRAVA_API_URL}/activities/{activity_id}", headers=headers
    )
    return response.json()


def get_gear(gear_id: str) -> dict:
    access_token = check_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{STRAVA_API_URL}/gear/{gear_id}", headers=headers)
    return response.json()


def classify_segments(segments: List[dict], frame_type: int) -> None:
    for segment in segments:
        segment_id = segment["segment"]["id"]
        if segment_id not in SEGMENTS:
            SEGMENTS[segment_id] = Counter()
        SEGMENTS[segment_id][frame_type] += 1


def store_activities(activities: List[str]) -> None:
    for activity_id in activities:
        if activity_id in ACTIVITIES:
            continue
        activity = get_activity(activity_id)
        ACTIVITIES[activity_id] = activity
    with open("activities.json", "w") as activities_file:
        json.dump(ACTIVITIES, activities_file)


def weigh_activities() -> None:
    for activity in ACTIVITIES.values():
        segments = activity["segment_efforts"]
        gear_id = activity["gear"]["id"]
        frame_type = BIKE_MAPPING[gear_id]["frame_type"]
        classify_segments(segments, frame_type)


def write_segments_to_file() -> None:
    with open("segment_scores.json", "w") as segments_file:
        json.dump(SEGMENTS, segments_file)


def read_segments_from_file() -> None:
    with open("segment_scores.json") as segments_file:
        global SEGMENTS
        SEGMENTS = json.load(segments_file)


def read_activities_from_file() -> None:
    with open("activities.json") as activities_file:
        global ACTIVITIES
        ACTIVITIES = json.load(activities_file)


def calculate_ride_scores(segments: List[dict]) -> Optional[str]:
    type_counter = Counter()
    for segment in segments:
        segment_id = str(segment["segment"]["id"])
        segment_scores = SEGMENTS.get(segment_id, {})
        for frame_type, count in segment_scores.items():
            type_counter[frame_type] += count
    most_common = type_counter.most_common(1)
    if not most_common:
        return None
    return FRAME_TYPE_TO_ID.get(most_common[0][0])


def update_gear_for_id(activity_id: str, gear_id: str) -> dict:
    access_token = check_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put(
        f"{STRAVA_API_URL}/activities/{activity_id}",
        headers=headers,
        json={"gear_id": gear_id},
    )
    return response.json()


if __name__ == "__main__":
    # get_activities()
    activities_to_store = [
        "6714333652",  # road
        "5962136667",  # road
        "5944650054",  # gravel
        "5848401428",  # road
        "5778498655",  # mtb
        "5628269530",  # mtb
        "5602416559",  # gravel
        "5571288565",  # gravel (maybe remove this one)
        "5514393873",  # mtb
        "5490803229",  # gravel
    ]
    # store_activities(activities_to_store)

    # NOTE: This weighs previous activities
    read_activities_from_file()
    read_segments_from_file()
    # weigh_activities()
    # write_segments_to_file()
    # activity = ACTIVITIES["6714333652"]
    activity_id = "5220891294"
    activity = get_activity(activity_id)
    segments = activity["segment_efforts"]
    gear_id = calculate_ride_scores(segments)
    response = update_gear_for_id(activity_id, gear_id)
    print(response)

    # print(len(activity["segment_efforts"]))
    # gear_id = activity.get("gear", {}).get("id")
    # gear_obj = get_gear(gear_id)
    # print(gear_obj)
