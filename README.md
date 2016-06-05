# pexgrabber

#### What is it?
pexgrabber is an example script that will grab the participant and conference history from a Pexip Management node and populates this information in a local database.

#### Why?
So that users may keep a local, rolling copy of the history for subsequent reporting.

#### What does it do?
1. Import config from a _config.ini_
2. Creates an sqlite3 database if one is not found (pexhistory.db)
3. Create and construct schemas for participant and conference tables in the database
4. Download participant and conference history from _last_downloaded_ till now (time of running the script)
5. Add current time to config so that the next run with download data from the last time it was downloaded.
6. Add participant and conference history to the database.
7. pexgrabber creates a rotating log called pexgrabber.log and will create a pexgrbber.log._x_ file when it reached 10MB
 
Use case would be to run this regularly using cron or celery
