from django.contrib import admin
from django.urls import path
from ezhuthu.views import MyView, Users, Lottery, LotteryByDate, TotalSale, Price, DeleteLottery
from django.urls import path, include

app_name = 'ezhuthu'

urlpatterns = [
    path('login/', MyView.as_view()),
    path('users/', Users.as_view()),
    path('lottery/', Lottery.as_view()),
    path('lottery-bydate/', LotteryByDate.as_view()),
    path('total-sale/', TotalSale.as_view()),
    path('price/', Price.as_view()),
    path('delete-lottery/', DeleteLottery.as_view()),
    
]