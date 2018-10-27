from django.shortcuts import render


# Create your views here.

# http://127.0.0.1:8000
def index(request):
    '''首页'''
    return render(request, 'index.html')


def goodinfo(request):
    """商品详情"""
    return render(request, 'product.html')


def goodlist(request):
    '''商品列表'''
    return render(request, 'store.html')