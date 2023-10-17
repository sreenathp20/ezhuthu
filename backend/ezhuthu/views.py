from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ezhuthu.db import Mongo
import json
from rest_framework_simplejwt.tokens import RefreshToken

import datetime
from datetime import timedelta
import jwt # import jwt library
import pytz 
IST = pytz.timezone('Asia/Kolkata') 


SECRET_KEY = "python_jwt"

COT = 15 # cut off time

# json data to encode




# Create your views here.

from django.http import HttpResponse
from django.views import View

def jsonify(data):
    d = []
    for di in data:
        d.append(di)
    return d

def decodeJwt(request):
    auth = request.headers['Authorization']
    token = auth.split(' ')[1]
    decoded_data = jwt.decode(jwt=token,
                              key=SECRET_KEY,
                              algorithms=["HS256"])
    return decoded_data

def joinUser(n, userDict):
    n['name'] = userDict[n['user']]
    return n

def mapUsers(data, client_id):
    m = Mongo()
    users = m.find("users", client_id)
    userDict = {}
    for u in users:
        userDict[u["_id"]] = u["name"]
    #data = [1,2]
    userDictList = list(map(lambda x: userDict, data))
    res = list(map(joinUser, data, userDictList))
    return res

def getStartAndEnd(date):
    if date.hour >= COT:
        start = datetime.datetime(date.year,date.month,date.day,COT,0,0)
        end_date = date + timedelta(days=1)
        end = datetime.datetime(end_date.year,end_date.month,end_date.day,COT-1,59,59)
    else:
        start_date = date - timedelta(days=1)
        start = datetime.datetime(start_date.year,start_date.month,start_date.day,COT,0,0)
        end = datetime.datetime(date.year,date.month,date.day,COT-1,59,59)
    return start, end

 
class MyView(View):

    def get_tokens_for_user(uself, user, id):
        json_data = {
            "userid": id,
            "username": user,
            "date": str(datetime.datetime.now())
        }
        encode_data = jwt.encode(payload=json_data, \
        key=SECRET_KEY, algorithm="HS256")

        return encode_data
    def get(self, request):
        # <view logic>
        return HttpResponse('result')
    
    @csrf_exempt
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)['data']
        m = Mongo()
        d = m.find_one("clients", data['username'], data['password'])
        if d:
            token = self.get_tokens_for_user(d['username'], d["_id"])
            res = {'username':data['username'], 'token': token, 'success': True}
        else:
            res = {'success': False}
        return JsonResponse(res)
    
class Users(View):
    def get(self, request):
        client = decodeJwt(request)
        m = Mongo()
        users = m.findUsers("users", client['userid'])
        users = jsonify(users)
        # <view logic>
        return JsonResponse(users, safe=False)
    
    @csrf_exempt
    def post(self, request):
        client = decodeJwt(request)
        m = Mongo()
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)['data']
        data['client_id'] = client['userid']
        m.insertUser("users", data)
        return JsonResponse({"message": "User created successfully", "success": True}, safe=False)
    
class Lottery(View):
    def get(self, request):
        client = decodeJwt(request)
        m = Mongo()
        date = datetime.datetime.now(IST)
        # if date.hour >= COT:
        #     start = datetime.datetime(date.year,date.month,date.day,COT,0,0)
        #     end_date = date + timedelta(days=1)
        #     end = datetime.datetime(end_date.year,end_date.month,end_date.day,COT-1,59,59)
        # else:
        #     start_date = date - timedelta(days=1)
        #     start = datetime.datetime(start_date.year,start_date.month,start_date.day,COT,0,0)
        #     end = datetime.datetime(date.year,date.month,date.day,COT-1,59,59)
        start, end = getStartAndEnd(date)
        lottery = m.findLottery("lottery", client['userid'], start, end)
        lottery = jsonify(lottery)
        lottery = mapUsers(lottery, client['userid'])
        # <view logic>
        return JsonResponse(lottery, safe=False)
    
    def post(self, request):
        client = decodeJwt(request)
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)['data']
        date = datetime.datetime.now(IST)
        iSet = data[0]['set']
        numbers = []
        numberDict = {}
        for d in data:
            int_number = int(d['number'])
            d['number'] = int_number
            numbers.append(int_number)
            numberDict[int_number] = d['count']
            d['client_id'] = client['userid']        
            d['date'] = datetime.datetime(date.year,date.month,date.day,date.hour,date.minute,date.second)
        m = Mongo()
        if iSet == 'ABC':
            val = self.validateSetCount(numbers, m, date, numberDict)
            if len(val) > 0:
                return JsonResponse({"message": str(val[0]['number'])+" count exceeds 200", "success": False}, safe=False)
        m.insertLottery("lottery", data)
        return JsonResponse({"message": "Lettery created successfully", "success": True}, safe=False)
    
    def validateSetCount(self, numbers, m, date, input):
        start, end = getStartAndEnd(date)
        data = m.getSetCount(numbers, start, end)
        numberDict = {}
        #for n in numbers:
        for d in data:
            number = d['number']
            if number in numberDict:
                numberDict[number] += d['count']
            else:
                numberDict[number] = d['count']
        res = []
        for k in numberDict.keys():
            cnt = numberDict[k]+input[k]
            if cnt > 200:
                res.append({"number": k, "count": cnt})

        return res
        pass
    
class LotteryByDate(View):
    def post(self, request):
        client = decodeJwt(request)
        m = Mongo()
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        date = data['date']
        d  = datetime.datetime(int(date.split('/')[2]),int(date.split('/')[1]),int(date.split('/')[0]))
        start_date = d - timedelta(days=1)
        start = datetime.datetime(start_date.year,start_date.month,start_date.day,COT,0,0)
        end_date = d
        end = datetime.datetime(end_date.year,end_date.month,end_date.day,COT-1,59,59)
        lottery = m.findLottery("lottery", client['userid'], start, end)
        lottery = jsonify(lottery)
        lottery = mapUsers(lottery, client['userid'])
        # <view logic>
        return JsonResponse(lottery, safe=False)
    
class TotalSale(View):
    def get(self, request):
        client = decodeJwt(request)
        m = Mongo()
        date = datetime.datetime.now(IST)
        start, end = getStartAndEnd(date)
        lottery = m.findLottery("lottery", client['userid'], start, end)
        lottery = jsonify(lottery)
        data = self.getTotalSale(lottery)
        # <view logic>
        return JsonResponse(data, safe=False)
    
    def getTotalSale(self, data):
        res = {"total": 0}
        total = 0
        for d in data:
            if d['set'] == 'A' or d['set'] == 'B' or d['set'] == 'C':
                t = d['count'] * 11
            else:
                t = d['count'] * 10
            total += t
        res['total'] = total
        return res

    
