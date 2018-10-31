from datetime import date

from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper

from db.base_model import BaseModel


# Create your models here.

class OrderNumberField(models.CharField):
    def get_db_prep_value(self, value, connection: BaseDatabaseWrapper, prepared=False) -> str:
        if not value:  # 避免 更新时 重新生成 单号
            cursor = connection.cursor()

            cursor.execute("select order_num from df_order_info ORDER by id DESC limit 0, 1")
            row = cursor.fetchone()  # 获取查询记录   返回是tuple

            current_date = date.strftime(date.today(), '%Y%m%d')

            if row:  # 空元组是没有记录的
                cn = row[0]
                date_, number = cn[:8], cn[8:]
                if date_ == current_date:
                    number = str(int(number)+1).rjust(4, '0')
                    return '%s%s' % (date_, number)

            return '%s0001' % current_date

        return value


class OrderInfo(BaseModel):
    '''订单模型类'''
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付'),
    )

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )

    order_num = OrderNumberField(max_length=20, verbose_name='单号')
    user = models.ForeignKey('user.User', verbose_name='用户', on_delete=models.CASCADE)
    addr = models.ForeignKey('user.Address', verbose_name='地址', on_delete=models.CASCADE)
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name='支付方式')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品运费')
    texes_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品税费')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    trade_no = models.CharField(max_length=128, verbose_name='支付编号')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    '''订单商品模型类'''
    order = models.ForeignKey('OrderInfo', verbose_name='订单', on_delete=models.CASCADE)
    sku = models.ForeignKey('goods.GoodsSKU', verbose_name='商品SKU', on_delete=models.CASCADE)
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=256, verbose_name='评论')

    class Meta:
        db_table= 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name


class OrderAfterSales(BaseModel):
    '''售后服务模型类'''
    SALES_RETURN_CHOICE = (
        (1,'退款'),
        (2,'退货'),
        (3,'换货'),
    )
    rel_order = models.ForeignKey('OrderGoods',verbose_name='订单商品',on_delete=models.CASCADE, default=1)
    service_type = models.SmallIntegerField(choices=SALES_RETURN_CHOICE, default=3, verbose_name='选择类型',null=True)
    After_review = models.TextField(max_length=200,verbose_name='售后评论', blank=True)
    picture = models.ImageField(upload_to='except_photo', verbose_name='上传照片')