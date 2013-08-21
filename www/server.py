import os, sys, time, json, logging, ConfigParser, pymongo
from flask import Flask, render_template
import jinja2

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from mcgeo.db import MongoGeoStoryDatabase

app = Flask(__name__)

cache = {}  # in-memory cache, controlled by _get_from_cache and _set_in_cache helpers

# setup logging
logging.basicConfig(filename='mc-server.log',level=logging.DEBUG)
log = logging.getLogger('mc-server')
log.info("---------------------------------------------------------------------------")

# connect to the database
config = ConfigParser.ConfigParser()
config.read(parentdir+'/mc-client.config')
try:
    db = MongoGeoStoryDatabase(config.get('db','name'),config.get('db','host'),int(config.get('db','port')))
except pymongo.errors.ConnectionFailure, e:
    log.error(e)
else:
    log.info("Connected to "+config.get('db','name')+" on "+config.get('db','host')+":"+str(config.get('db','port')))

@app.route("/")
def index():
    count_by_country = db.storyCountByCountryCode()
    story_count = db.storyCount()
    return render_template("base.html",
        story_count = story_count,
        located_story_count = sum(count_by_country.values()),
        count_by_country_json = json.dumps(count_by_country)
    )

def _get_from_cache(key, max_age=86400):
    if key in cache:
        if time.mktime(time.gmtime()) - cache[key]['time'] < max_age:
            return cache[key]['value']
    return None

def _set_in_cache(key, value):
    cache[key] = {
        'value': value,
        'time': time.mktime(time.gmtime())
    }

if __name__ == "__main__":
    app.debug = True
    app.run()
