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
        raw_results = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(raw_results,'media_id')

    def mentionedStoryCountByMediaSource(self, country_code):
        mapper = Code("""
               function () {
                 var countryCode = '"""+country_code+"""';
                 if(countryCode in this.country_mentions){
                    emit(this.media_id,this.country_mentions[countryCode]);
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
        key = ['country_code']
        condition = None
        if media_id is not None:
            condition = {'media_id': int(media_id)}    
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        raw_results = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(raw_results,'country_code')

    def mentionedStoryCountByCountry(self,media_id=None):
        extraJS = "";
        if media_id is not None:
            extraJS =  "if(this.media_id!="+media_id+") return;"
        mapper = Code("""
               function () {
                 """+extraJS+"""
                 for(var countryCode in this.country_mentions){
                    if(countryCode.length==2){
                        emit(countryCode,this.country_mentions[countryCode]);
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
