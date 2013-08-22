import math
from mediacloud.storage import MongoStoryDatabase
from bson.code import Code

class MongoGeoStoryDatabase(MongoStoryDatabase):
    '''
    Simply supports the server example by making queries easier
    '''

    def storyCountByMediaSource(self, country_code):
        key = ['media_id']
        condition = {'country_code': country_code}
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        rawResults = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(rawResults,'media_id')

    def storyCountByCountry(self, media_id):
        key = ['country_code']
        condition = {'media_id': int(media_id)}
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        rawResults = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(rawResults,'country_code')

    def storyCountByCountryCode(self):
        key = ['country_code']
        condition = None
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        rawResults = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(rawResults,'country_code')

    # assumes key is integer!
    def _resultsToDict(self, rawResults, id_key):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in rawResults:
            key_ok = False
            try:
                # first make sure key is an integer
                throwaway = doc[id_key]
                # now check optional range
                if throwaway=='?' or throwaway=='NULL':
                    key_ok = False
                else:
                    key_ok = True
            except:
                # we got NaN, so ignore it
                key_ok = False
            if key_ok:
                results[ doc[id_key] ] = int(doc['value'])
        return results
