# Gear Autoselector

If you're like me you ride different bikes in different situations. It's annoying that Strava can't just read my mind as to which bike I rode for a given activity.  Leaving me to go in to the activity manually and switch the activity.


This app works by looking at some of your manually classified routes and weighting segments done on them.  The idea is if you've only done most of a ride on a mountain bike previously the end ride is classified as a mountain bike.


Things Left to do:
1. Dockerize the application
1. Listen for webhook
1. Update description when changes have been made
1. UI to allow reclassifying of rides if window has expired.
1. Document flow the application
1. Setup crons
1. backfill scheduler
1. Add support for other gear types
1. Check scope on redirect to make sure we have the permissions we need.
1. Scheduler check for reclassification
1. Add check for rate limit
1. make user id unique
1. document needed environment variables
1. Add a what's next page after redirect.
1. Add tests.