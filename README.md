# pexgrabber

#### What is it?
pexgrabber is an example script that will grab the participant and conference history from a Pexip Management node and populates this information in a local database.

#### Why?
So that users may keep a local, rolling copy of the history for subsequent reporting.

#### What does it do?
1. Import config from a _config.ini_
2. Creates an sqlite3 database if one is not found (pexhistory.db)
3. Create and construct schemas for participant and conference tables in the database
