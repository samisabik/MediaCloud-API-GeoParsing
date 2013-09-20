import clavin

'''
'''

def addLocationsToStory(db_story, raw_story):
    # stitch the story back together
    sentences = [ s['sentence'] for s in raw_story['story_sentences']]
    text = '  '.join(sentences)
    response = clavin.locate(text)
    if response['status']=='ok':
        db_story['locations'] = response['results']
        # determine most-mentioned country
        max_country = {'country': '?','mentions':0}
        country_mentions = {}
        for item in response['results']:
            country = item['countryCode']
            if country not in country_mentions:
                country_mentions[country] = 0
            country_mentions[country] += 1
        country_mention_array = []
        for country in country_mentions:
            if country_mentions[country] > max_country['mentions']:
                max_country = {'country': country,'mentions': country_mentions[country]}
            country_mention_array.append( {'country_code':country, 'mention_count':country_mentions[country]} )

        db_story['country_code'] = max_country['country']
        db_story['country_mentions'] = country_mention_array
