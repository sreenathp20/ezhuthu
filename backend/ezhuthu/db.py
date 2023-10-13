import pymongo
#connect_string = 'mongodb+srv://<username>:<password>@<atlas cluster>/<myFirstDatabase>?retryWrites=true&w=majority' 
connect_string = 'mongodb://localhost' 
from django.conf import settings
my_client = pymongo.MongoClient(connect_string)


class Mongo:
    def __init__(self) -> None:
        self.dbname = my_client['ezhuthu']

        pass

    def insert(self, collection, data):
        collection_name = self.dbname[collection]
        find = collection_name.find().sort('date', -1).limit(1)
        if find:
            c = find[0]['_id']
            data['_id'] = c+1
        else:
            data['_id'] = 1
        collection_name.insert_many([data])

    def insertUser(self, collection, data):
        collection_name = self.dbname[collection]
        find = collection_name.find().sort('_id', -1).limit(1)
        if find:
            c = find[0]['_id']
            data['_id'] = c+1
        else:
            data['_id'] = 1
        collection_name.insert_many([data])

    def find_one(self, collection, username, password):
        collection_name = self.dbname[collection]
        return collection_name.find_one({"username": username, "password": password})
    
    def find(self, collection, user_id):
        collection_name = self.dbname[collection]
        return collection_name.find({"client_id": user_id})
    
    def findUsers(self, collection, user_id):
        collection_name = self.dbname[collection]
        return collection_name.find({"client_id": user_id}).sort('name', 1)
    
    def findLottery(self, collection, user_id, start, end):
        collection_name = self.dbname[collection]
        return collection_name.find({"client_id": user_id, "date": {"$gte":start, "$lt": end}}).sort("date", -1)


