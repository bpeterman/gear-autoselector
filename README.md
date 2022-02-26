# Gear Autoselector

If you're like me you ride different bikes in different situations. It's annoying that Strava can't just read my mind as to which bike I rode for a given activity.  Leaving me to go in to the activity manually and switch the activity.


This app works by looking at some of your manually classified routes and weighting segments done on them.  The idea is if you've only done most of a ride on a mountain bike previously the end ride is classified as a mountain bike.


Things Left to do:
* Dockerize the application
* UI for sign up?
* Move storage to Django ORM tables
* Listen for webhook
* Scheduler check for reclassification
* Update description when changes have been made
* UI to allow reclassifying of rides if window has expired.
* backfill scheduler
* Add guard to only check for bike rides
* Add support for other gear types