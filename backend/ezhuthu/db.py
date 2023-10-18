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
        find = list(collection_name.find().sort('date', -1).limit(1))
        if find:
            c = find[0]['_id']
            data['_id'] = c+1
        else:
            data['_id'] = 1
        collection_name.insert_many([data])

    def insertPrice(self, data):
        collection_name = self.dbname['price']
        find = list(collection_name.find().sort('_id', -1).limit(1))
        if find:
            c = find[0]['_id']
            i = 1
            data['_id'] = c+i
        else:
            i = 1
            data['_id'] = i
        collection_name.insert_many([data])

    def updatePrice(self, start, end, data):
        collection_name = self.dbname['lottery']
        lottery = list(collection_name.find({"date": {"$gte":start, "$lt": end}}).sort("date", -1))
        upd = []
        for l in lottery:
            number = l['number']
            cnt = l['count']
            id = l['_id']
            price = 0
            set = l['set']
            if set == 'ABC':
                if number == int(data['first']):
                    price = 5000 * cnt
                if number == int(data['second']):
                    price = 500 * cnt
                if number == int(data['third']):
                    price = 250 * cnt
                if number == int(data['fourth']):
                    price = 100 * cnt
                if number == int(data['fifth']):
                    price = 50 * cnt
                if str(number) in data['compliments']:
                    price = 30 * cnt
            if set == 'A':
                if str(number) == str(data['first'])[0]:
                    price = 100 * cnt
            if set == 'B':
                if str(number) == str(data['first'])[1]:
                    price = 100 * cnt
            if set == 'C':
                if str(number) == str(data['first'])[2]:
                    price = 100 * cnt
            if set == 'AB':
                number = str(number)
                res = str(data['first'])[0]+str(data['first'])[1]
                if number == res:
                    price = 600 * cnt
            if set == 'AC':
                number = str(number)
                res = str(data['first'])[0]+str(data['first'])[2]
                if number == res:
                    price = 600 * cnt
            if set == 'BC':
                number = str(number)
                res = str(data['first'])[1]+str(data['first'])[2]
                if number == res:
                    price = 600 * cnt
            upd.append({"price": price, "_id": id})
        for u in upd:
            filter = { '_id': u['_id'] }
            newvalues = { "$set": { 'price': u['price'] } }
            collection_name.update_one(filter, newvalues) 
                
                    
    def deleteLottery(self, id):
        collection_name = self.dbname['lottery']
        myQuery ={'_id':id}
        collection_name.delete_one(myQuery)

    def insertLottery(self, collection, data):
        collection_name = self.dbname[collection]
        find = list(collection_name.find().sort('_id', -1).limit(1))
        if find:
            c = find[0]['_id']
            i = 1
            for d in data:
                d['_id'] = c+i
                i += 1
        else:
            i = 1
            for d in data:
                d['_id'] = i
                i += 1
        collection_name.insert_many(data)

    def insertUser(self, collection, data):
        collection_name = self.dbname[collection]
        find = list(collection_name.find().sort('_id', -1).limit(1))
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
    
    def findPrice(self, collection):
        collection_name = self.dbname[collection]
        return collection_name.find().sort('date', -1)
    
    def findLottery(self, collection, user_id, start, end):
        collection_name = self.dbname[collection]
        return collection_name.find({"client_id": user_id, "date": {"$gte":start, "$lt": end}}).sort("date", -1)
    
    def getSetCount(self, numbers, start, end):
        collection_name = self.dbname['lottery']
        res = list(collection_name.find({"number": {"$in": numbers}, "date": {"$gte":start, "$lt": end}}).sort("date", -1))
        return res
    
    def getPrice(self, date):
        collection_name = self.dbname['price']
        res = list(collection_name.find({"date": date}).sort("date", -1))
        return res



