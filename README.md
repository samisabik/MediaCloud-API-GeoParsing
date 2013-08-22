MediaCloud Python Geo
=====================

Installation
------------

First [download the latest zip of the python api client module](https://github.com/c4fcm/MediaCloud-API-Client/tree/master/dist) 
and install it like this:

    python setup.py install

Now to run these examples make sure you have Python > 2.6 (and setuptools) and then install 
some python modules:

Now to run these examples make sure you have Python > 2.6 (and setuptools) and then install 
some python modules:
    
    easy_install pypubsub requests unicodecsv pymongo couchdb
    
Install [MongoDb](http://mongodb.org) to store article info.

Copy the `mc-client.config.template` to `mc-client.config` and edit it, putting in the 
API username and password, and database connection settings too.

