from django.http import HttpResponseRedirect
from django.shortcuts import render
from apps.order.models import *
from utils.mixin import LoginRequiredMixin


class refund_type(LoginRequiredMixin):
    '''售后服务页面显示'''
    def post(self,request):
        '''售后服务详情页显示'''
        # 获取登陆的用户
        user = request.user
        # 获取参数sku_ids
        order_id = request.POST.getlist('order_id')
        aftersales = OrderAfterSales.objects.get(id=order_id)
        if not aftersales:
            # 校验参数
            type = request.POST.get("rd")
            text = request.POST.get("text1")
            photo = request.POST.get('photo')
            if type=="退款":
                OrderAfterSales.objects.create(service_type=type,
                                               After_review=text,
                                               picture = photo )
                return render(request, 'yemianbuju.html', {'errmsg': '退款信息提交成功!'})
            elif type=="换货":
                OrderAfterSales.objects.create(service_type=type,
                                               After_review=text,
                                               picture=photo)
                return render(request, 'yemianbuju.html', {'errmsg': '换货信息提交成功!'})
            elif type=="退货":
                OrderAfterSales.objects.create(service_type=type,
                                               After_review=text,
                                               picture=photo)
                return render(request, 'yemianbuju.html', {'errmsg': '退货信息提交成功!'})
        else:
            return render(request,'yemianbuju.html', {'errmsg':'没有找到此商品的信息'})
