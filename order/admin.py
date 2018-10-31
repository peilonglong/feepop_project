from django.contrib import admin

# Register your models here.
from order.models import OrderInfo,OrderGoods,OrderAfterSales

admin.site.register([OrderInfo,OrderGoods,OrderAfterSales])