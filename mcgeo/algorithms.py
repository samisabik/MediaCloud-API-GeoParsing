import clavin

'''
'''

def addLocationsToStory(db_story, raw_story):
    # stitch the story back together
    sentences = [ s['sentence'] for s in raw_story['story_sentences']]
    text = '  '.join(sentences)
    response = clavin.locate(text)
    if response['status']=='ok':
        # determine most-mentioned country
        country_mentions = {}
        for item in response['places']:
            country = item['countryCode']
            if country not in country_mentions:
                country_mentions[country] = 0
            country_mentions[country] += 1
        country_mention_array = []
        for country in country_mentions:
            country_mention_array.append( {'country_code':country, 'mention_count':country_mentions[country]} )

        db_story['geo_places'] = response['places']
        db_story['geo_country_mentions'] = country_mention_array
        db_story['geo_primary_country'] = None
        if len(response['primaryCountries'])>0:
            db_story['geo_primary_country'] = response['primaryCountries'][0]
