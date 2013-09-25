import math
from mediacloud.storage import MongoStoryDatabase
from bson.code import Code

class MongoGeoStoryDatabase(MongoStoryDatabase):
    '''
    Simply supports the server example by making queries easier
    '''

    def storyCountByMediaSource(self, country_code):
        key = ['media_id']
        condition = {'geo_primary_country': country_code}
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        raw_results = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(raw_results,'media_id')

    def mentionedStoryCountByMediaSource(self, country_code):
        mapper = Code("""
               function () {
                 var countryCode = '"""+country_code+"""';
                 for(var idx in this.geo_country_mentions){
                    var mention = this.geo_country_mentions[idx];
                    if(countryCode==mention.geo_primary_country){
                      emit(this.media_id, mention.mention_count);
                    }
                 }
               }
               """)
        reducer = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
                """)
        results = self._db.stories.map_reduce(mapper,reducer, "mentionedStoryCountByMediaSource")
        docs = []
        for doc in results.find():
            docs.append(doc)
        return self._resultsToDict(docs,'_id')        

    def storyCountByCountry(self, media_id=None):
        key = ['geo_primary_country']
        condition = None
        if media_id is not None:
            condition = {'media_id': int(media_id)}    
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        raw_results = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(raw_results,'geo_primary_country')

    def countryStories(self, country_code, media_id=None):
        criteria = {'geo_primary_country': country_code}
        if media_id is not None:
          criteria['media_id'] = int(media_id)
        docs = []
        for doc in self._db.stories.find(criteria):
            docs.append(doc)
        return docs

    def mentionedCountryStories(self, country_code, media_id=None):
        # http://docs.mongodb.org/manual/reference/method/db.collection.find/
        criteria = {'geo_country_mentions': {
          '$elemMatch': {
            'country_code': country_code
          }
        }}
        if media_id is not None:
          criteria['media_id'] = int(media_id)
        docs = []
        for doc in self._db.stories.find(criteria):
            docs.append(doc)
        return docs

    def mentionedStoryCountByCountry(self,media_id=None):
        extraJS = "";
        if media_id is not None:
            extraJS =  "if(this.media_id!="+media_id+") return;"
        mapper = Code("""
               function () {
                 """+extraJS+"""
                 for(var idx in this.geo_country_mentions){
                    var mention = this.geo_country_mentions[idx];
                    if(mention.country_code.length==2){
                        emit(mention.country_code,mention.mention_count);
                    }
                 }
               }
               """)
        reducer = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
                """)
        results = self._db.stories.map_reduce(mapper,reducer, "mentionedStoryCountByCountry")
        docs = []
        for doc in results.find():
            docs.append(doc)
        return self._resultsToDict(docs,'_id')

    # assumes key is integer!
    def _resultsToDict(self, raw_results, id_key):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in raw_results:
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
