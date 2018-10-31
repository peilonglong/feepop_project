from django.contrib import admin

# Register your models here.
from goods.models import GoodsType, Goods, GoodsSKU, GoodsImage, IndexTypeGoodsBanner, IndexPromotionBanner, IndexGoodsBanner

admin.site.register([GoodsType, Goods, GoodsSKU, GoodsImage, IndexTypeGoodsBanner, IndexPromotionBanner, IndexGoodsBanner])