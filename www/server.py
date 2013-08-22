import os, sys, time, json, logging, ConfigParser, pymongo
from operator import itemgetter
from flask import Flask, render_template
import jinja2
import mediacloud

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from mcgeo.db import MongoGeoStoryDatabase

USE_MENTIONED = True

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
    if USE_MENTIONED:
        count_by_country = db.mentionedStoryCountByCountry()
    else:
        count_by_country = db.storyCountByCountry()
    story_count = db.storyCount()
    return render_template("global-map.html",
        story_count = story_count,
        located_story_count = sum(count_by_country.values()),
        count_by_country_json = json.dumps(count_by_country)
    )

@app.route("/country/<country_code>/media-coverage")
def country_media_coverage(country_code):
    if USE_MENTIONED:
        story_count_by_media = db.mentionedStoryCountByMediaSource(country_code)
    else:
        story_count_by_media = db.storyCountByMediaSource(country_code)
    detailed_counts = []
    for media_id in story_count_by_media.keys():
        detailed_counts.append({
            'id': int(media_id),
            'name': mediacloud.api.mediaSource(int(media_id))['name'],
            'story_count': story_count_by_media[media_id]
        })
    return render_template("country-media-coverage.html",
        country_code = country_code,
        country_name = _country_name(country_code),
        coverage = sorted(detailed_counts,key=itemgetter('story_count'), reverse=True),
        story_count = sum(story_count_by_media.values())
    )

@app.route("/media/<media_id>/country-coverage")
def media_country_coverage(media_id):
    if USE_MENTIONED:
        count_by_country = db.mentionedStoryCountByCountry(media_id)
    else:
        count_by_country = db.storyCountByCountry(media_id)
    detailed_counts = []
    for country_code in count_by_country.keys():
        detailed_counts.append({
            'country_code': country_code,
            'country_name': _country_name(country_code),
            'story_count': count_by_country[country_code]
        })
    return render_template("media-country-coverage.html",
        media_info = mediacloud.api.mediaSource(int(media_id)),
        coverage = sorted(detailed_counts,key=itemgetter('story_count'), reverse=True),
        story_count = sum(count_by_country.values())
    )

country_code_to_name = { 'AD': "Andorra", 'AE': "United Arab Emirates", 'AF': "Afghanistan", 'AG': "Antigua and Barbuda", 'AI': "Anguilla", 'AL': "Albania", 'AM': "Armenia", 'AO': "Angola", 'AQ': "Antarctica", 'AR': "Argentina", 'AS': "American Samoa", 'AT': "Austria", 'AU': "Australia", 'AW': "Aruba", 'AX': "Aland Islands", 'AZ': "Azerbaijan", 'BA': "Bosnia and Herzegovina", 'BB': "Barbados", 'BD': "Bangladesh", 'BE': "Belgium", 'BF': "Burkina Faso", 'BG': "Bulgaria", 'BH': "Bahrain", 'BI': "Burundi", 'BJ': "Benin", 'BL': "Saint Barthelemy", 'BM': "Bermuda", 'BN': "Brunei", 'BO': "Bolivia", 'BQ': "Bonaire, Saint Eustatius and Saba ", 'BR': "Brazil", 'BS': "Bahamas", 'BT': "Bhutan", 'BV': "Bouvet Island", 'BW': "Botswana", 'BY': "Belarus", 'BZ': "Belize", 'CA': "Canada", 'CC': "Cocos Islands", 'CD': "Democratic Republic of the Congo", 'CF': "Central African Republic", 'CG': "Republic of the Congo", 'CH': "Switzerland", 'CI': "Ivory Coast", 'CK': "Cook Islands", 'CL': "Chile", 'CM': "Cameroon", 'CN': "China", 'CO': "Colombia", 'CR': "Costa Rica", 'CU': "Cuba", 'CV': "Cape Verde", 'CW': "Curacao", 'CX': "Christmas Island", 'CY': "Cyprus", 'CZ': "Czech Republic", 'DE': "Germany", 'DJ': "Djibouti", 'DK': "Denmark", 'DM': "Dominica", 'DO': "Dominican Republic", 'DZ': "Algeria", 'EC': "Ecuador", 'EE': "Estonia", 'EG': "Egypt", 'EH': "Western Sahara", 'ER': "Eritrea", 'ES': "Spain", 'ET': "Ethiopia", 'FI': "Finland", 'FJ': "Fiji", 'FK': "Falkland Islands", 'FM': "Micronesia", 'FO': "Faroe Islands", 'FR': "France", 'GA': "Gabon", 'GB': "United Kingdom", 'GD': "Grenada", 'GE': "Georgia", 'GF': "French Guiana", 'GG': "Guernsey", 'GH': "Ghana", 'GI': "Gibraltar", 'GL': "Greenland", 'GM': "Gambia", 'GN': "Guinea", 'GP': "Guadeloupe", 'GQ': "Equatorial Guinea", 'GR': "Greece", 'GS': "South Georgia and the South Sandwich Islands", 'GT': "Guatemala", 'GU': "Guam", 'GW': "Guinea-Bissau", 'GY': "Guyana", 'HK': "Hong Kong", 'HM': "Heard Island and McDonald Islands", 'HN': "Honduras", 'HR': "Croatia", 'HT': "Haiti", 'HU': "Hungary", 'ID': "Indonesia", 'IE': "Ireland", 'IL': "Israel", 'IM': "Isle of Man", 'IN': "India", 'IO': "British Indian Ocean Territory", 'IQ': "Iraq", 'IR': "Iran", 'IS': "Iceland", 'IT': "Italy", 'JE': "Jersey", 'JM': "Jamaica", 'JO': "Jordan", 'JP': "Japan", 'KE': "Kenya", 'KG': "Kyrgyzstan", 'KH': "Cambodia", 'KI': "Kiribati", 'KM': "Comoros", 'KN': "Saint Kitts and Nevis", 'KP': "North Korea", 'KR': "South Korea", 'XK': "Kosovo", 'KW': "Kuwait", 'KY': "Cayman Islands", 'KZ': "Kazakhstan", 'LA': "Laos", 'LB': "Lebanon", 'LC': "Saint Lucia", 'LI': "Liechtenstein", 'LK': "Sri Lanka", 'LR': "Liberia", 'LS': "Lesotho", 'LT': "Lithuania", 'LU': "Luxembourg", 'LV': "Latvia", 'LY': "Libya", 'MA': "Morocco", 'MC': "Monaco", 'MD': "Moldova", 'ME': "Montenegro", 'MF': "Saint Martin", 'MG': "Madagascar", 'MH': "Marshall Islands", 'MK': "Macedonia", 'ML': "Mali", 'MM': "Myanmar", 'MN': "Mongolia", 'MO': "Macao", 'MP': "Northern Mariana Islands", 'MQ': "Martinique", 'MR': "Mauritania", 'MS': "Montserrat", 'MT': "Malta", 'MU': "Mauritius", 'MV': "Maldives", 'MW': "Malawi", 'MX': "Mexico", 'MY': "Malaysia", 'MZ': "Mozambique", 'NA': "Namibia", 'NC': "New Caledonia", 'NE': "Niger", 'NF': "Norfolk Island", 'NG': "Nigeria", 'NI': "Nicaragua", 'NL': "Netherlands", 'NO': "Norway", 'NP': "Nepal", 'NR': "Nauru", 'NU': "Niue", 'NZ': "New Zealand", 'OM': "Oman", 'PA': "Panama", 'PE': "Peru", 'PF': "French Polynesia", 'PG': "Papua New Guinea", 'PH': "Philippines", 'PK': "Pakistan", 'PL': "Poland", 'PM': "Saint Pierre and Miquelon", 'PN': "Pitcairn", 'PR': "Puerto Rico", 'PS': "Palestinian Territory", 'PT': "Portugal", 'PW': "Palau", 'PY': "Paraguay", 'QA': "Qatar", 'RE': "Reunion", 'RO': "Romania", 'RS': "Serbia", 'RU': "Russia", 'RW': "Rwanda", 'SA': "Saudi Arabia", 'SB': "Solomon Islands", 'SC': "Seychelles", 'SD': "Sudan", 'SS': "South Sudan", 'SE': "Sweden", 'SG': "Singapore", 'SH': "Saint Helena", 'SI': "Slovenia", 'SJ': "Svalbard and Jan Mayen", 'SK': "Slovakia", 'SL': "Sierra Leone", 'SM': "San Marino", 'SN': "Senegal", 'SO': "Somalia", 'SR': "Suriname", 'ST': "Sao Tome and Principe", 'SV': "El Salvador", 'SX': "Sint Maarten", 'SY': "Syria", 'SZ': "Swaziland", 'TC': "Turks and Caicos Islands", 'TD': "Chad", 'TF': "French Southern Territories", 'TG': "Togo", 'TH': "Thailand", 'TJ': "Tajikistan", 'TK': "Tokelau", 'TL': "East Timor", 'TM': "Turkmenistan", 'TN': "Tunisia", 'TO': "Tonga", 'TR': "Turkey", 'TT': "Trinidad and Tobago", 'TV': "Tuvalu", 'TW': "Taiwan", 'TZ': "Tanzania", 'UA': "Ukraine", 'UG': "Uganda", 'UM': "United States Minor Outlying Islands", 'US': "United States", 'UY': "Uruguay", 'UZ': "Uzbekistan", 'VA': "Vatican", 'VC': "Saint Vincent and the Grenadines", 'VE': "Venezuela", 'VG': "British Virgin Islands", 'VI': "U.S. Virgin Islands", 'VN': "Vietnam", 'VU': "Vanuatu", 'WF': "Wallis and Futuna", 'WS': "Samoa", 'YE': "Yemen", 'YT': "Mayotte", 'ZA': "South Africa", 'ZM': "Zambia", 'ZW': "Zimbabwe", 'CS': "Serbia and Montenegro", 'AN': "Netherlands Antilles" }
def _country_name(country_code):
    return country_code_to_name[country_code]

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
