import requests
import json
import urllib
from datetime import datetime, date, timedelta
import sqlite3
import os
from configobj import ConfigObj
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import glob
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler

## Logging settings
logging.basicConfig(filename='pexgrabber.log',
                    format='%(asctime)s %(message)s',
                    level=logging.INFO)
handler = RotatingFileHandler('pexgrabber.log', maxBytes=10000000,
                                  backupCount=5)

logger = logging.getLogger(__name__)
logger.addHandler(handler)

## Get config:
config = ConfigObj("config.ini")
start = config["Settings"]["last_downloaded"]
now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
user = config["Settings"]["user"]
password = config["Settings"]["password"]
mgr_address = config["Settings"]["mgr_address"]

## Write current time to config file as last_downloaded:
if now != config["Settings"]["last_downloaded"]:
    config["Settings"]["last_downloaded"] = now
    logger.info('Setting start time to: %s', now)

    try:
        with open("config.ini", "w") as cfg:
            config.write(cfg)
    except IOError:
        print "Error writing file!"
        pass

if not os.path.exists("pexhistory.db"):
    ## Create the database:
    logger.info('No database yet, creating database')
    db = sqlite3.connect("pexhistory.db")
    c = db.cursor()
    ## Create the participants table and it's schema:
    c.execute('''create table participantHist
                ("protocol" varchar(6) NOT NULL,
                 "disconnect_reason" varchar(250) NOT NULL,
                 "service_tag" varchar(250),
                 "bandwidth" integer,
                 "license_count" integer NOT NULL,
                 "conference_name" varchar(250) NOT NULL,
                 "duration" integer,
                 "media_node" varchar(50) NOT NULL,
                 "id" varchar(200) NOT NULL UNIQUE,
                 "display_name" varchar(1000) NOT NULL,
                 "remote_port" integer NOT NULL,
                 "signalling_node" varchar(50) NOT NULL,
                 "encryption" varchar(7) NOT NULL,
                 "parent_id" varchar(200),
                 "role" varchar(7) NOT NULL,
                 "service_type" varchar(28) NOT NULL,
                 "vendor" varchar(200) NOT NULL,
                 "is_streaming" bool NOT NULL,
                 "start_time" datetime,
                 "remote_address" varchar(50) NOT NULL,
                 "has_media" bool NOT NULL,
                 "system_location" varchar(250) NOT NULL,
                 "local_alias" varchar(1000) NOT NULL,
                 "call_direction" varchar(3) NOT NULL,
                 "remote_alias" varchar(1000) NOT NULL,
                 "end_time" datetime,
                 "call_uuid" varchar(200) NOT NULL)''')
    ## Create the conference table and it's schema:
    c.execute('''create table conferenceHist
              (
                "name" varchar(250) NOT NULL,
                "start_time" datetime,
                "duration" integer,
                "tag" varchar(250),
                "end_time" datetime,
                "instant_message_count" integer NOT NULL,
                "service_type" varchar(28) NOT NULL,
                "id" varchar(200) NOT NULL UNIQUE)''')

def savePartData(part):
    ## Save participant data to database:
    conn = sqlite3.connect("pexhistory.db")
    cursor = conn.cursor()
    logger.info('Adding participant: %s %s', part['display_name'], part["call_uuid"])

    cursor.execute('''INSERT INTO participantHist VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (part["protocol"],
                         part["disconnect_reason"],
                         part["service_tag"],
                         part["bandwidth"],
                         part["license_count"],
                         part["conference_name"],
                         part["duration"],
                         part["media_node"],
                         part["id"],
                         part["display_name"],
                         part["remote_port"],
                         part["signalling_node"],
                         part["encryption"],
                         part["parent_id"],
                         part["role"],
                         part["service_type"],
                         part["vendor"],
                         part["is_streaming"],
                         part["start_time"],
                         part["remote_address"],
                         part["has_media"],
                         part["system_location"],
                         part["local_alias"],
                         part["call_direction"],
                         part["remote_alias"],
                         part["end_time"],
                         part["call_uuid"],)
               )
    conn.commit()
    conn.close()

def saveConfData(conf):
    ## Save conference data to database:
    conn = sqlite3.connect("pexhistory.db")
    cursor = conn.cursor()

    logger.info('Adding conference: %s %s', conf["name"], conf["id"])

    cursor.execute('''INSERT INTO conferenceHist VALUES(?, ?, ?, ?, ?, ?, ?, ?)''',
                        (
                        conf["name"],
                        conf["start_time"],
                        conf["duration"],
                        conf["tag"],
                        conf["end_time"],
                        conf["instant_message_count"],
                        conf["service_type"],
                        conf["id"],)
               )
    conn.commit()
    conn.close()

def getParticipants():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url = "https://%s/api/admin/history/v1/participant/?limit=5000&end_time__gte=%s&end_time__lt=%s" % (mgr_address, start, now)
    response = requests.get(
        url,
        auth=(user, password),
        verify=False
        )
    participants = json.loads(response.text)['objects']
    for part in participants:
        savePartData(part)

def getConferences():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url = "https://%s/api/admin/history/v1/conference/?limit=5000&end_time__gte=%s&end_time__lt=%s" % (mgr_address, start, now)
    response = requests.get(
        url,
        auth=(user, password),
        verify=False
        )
    conferences = json.loads(response.text)['objects']

    for conf in conferences:
        saveConfData(conf)

if __name__ == "__main__":
    getParticipants()
    getConferences()
