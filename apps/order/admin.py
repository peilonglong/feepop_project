from django.contrib import admin
from order.models import OrderInfo, OrderGoods

admin.site.register([OrderInfo, OrderGoods])