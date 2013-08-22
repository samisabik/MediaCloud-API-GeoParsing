#! /usr/bin/env python
import time
start_time = time.time()

import ConfigParser
from pubsub import pub
import logging
import socket
import sys
import pymongo

from mediacloud.api import MediaCloud
from mediacloud.storage import *
import mcgeo.algorithms
import clavin

'''
This example is meant to be run from a cron job on a server. It fetches all stories 
created page by page. It saves the metadata for all those to a 'mediacloud' database.
'''

MAX_PAGES_TO_FETCH = 1
CONFIG_FILENAME = 'mc-client.config'

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILENAME)

# setup logging
logging.basicConfig(filename='mc-geo.log',level=logging.DEBUG)
log = logging.getLogger('mc-realtime')
log.info("---------------------------------------------------------------------------")

# setup a connection to the DB
try:
    db = MongoStoryDatabase(config.get('db','name'),config.get('db','host'),int(config.get('db','port')))
except pymongo.errors.ConnectionFailure, e:
    log.error(e)
    sys.exit()
log.info("Connected to "+config.get('db','name')+" on "+config.get('db','host')+":"+str(config.get('db','port')))

# setup a connection to the geocoder
worked = clavin.connect()
if not worked:
    sys.exit()

# setup the mediacloud connection
mc = MediaCloud( config.get('api','user'), config.get('api','pass') )

# set up my callback function that adds the reading grade level to the story
pub.subscribe(mcgeo.algorithms.addLocationsToStory, StoryDatabase.EVENT_PRE_STORY_SAVE)

# save all the stories in the db (this will fire the callback above)
saved = 0
first_page = int(config.get('api','first_page'))+1
for page in xrange(MAX_PAGES_TO_FETCH):
    query_page = first_page+(page+1)
    results = mc.allProcessed(query_page)
    log.info("Fetched "+str(len(results))+" stories (page "+str(query_page)+")")
    for story in results:
        worked = db.addStory(story)
        if worked:
            saved = saved + 1
        else:
            log.warning("    unable to save story "+str(story['stories_id'])) # prob exists already
    config.set('api','first_page',query_page)
    with open(CONFIG_FILENAME,'wb') as config_file_handle: 
        config.write(config_file_handle)

max_story_id = db.getMaxStoryId()

# log some performance stats
end_time = time.time()
duration = end_time - start_time
log.info("Saved "+str(saved)+" stories - new max id "+str(max_story_id))
if saved > 0:
    log.info("    took "+str(duration)+" secs ("+str(round(duration/saved,2))+" secs per story)")
