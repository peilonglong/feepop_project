from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
import re
from apps.user.models import User
from celery_tasks.tasks import send_register_active_email
from django.views.generic import View
from django.http import HttpResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings


class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        if request.method == 'GET':
            return render(request, 'register.html')
        else:
            '''进行注册处理'''
            # 接受数据
            username = request.POST.get('user_name')
            password = request.POST.get('pwd')
            email = request.POST.get('email')
            allow = request.POST.get('allow')

            # 进行数据校验
            if not all([username, password, email]):
                # 数据不完整
                return render(request, 'register.html', {'errmsg': '数据不完整'})
            # 校验邮箱
            if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
                return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

            if allow != 'on':
                return render(request, 'register.html', {'errmsg': '请同意协议'})

            # 校验用户名是否重复
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 用户名不存在
                user = None
            if user:
                # 用户名已存在
                return render(request, 'register.html', {'errmsg': '用户名已存在!'})

            # 进行业务处理: 进行用户注册
            user = User.objects.create_user(username, email, password)
            user.is_active = 0
            user.save()

            # 发送激活邮件: 包含激活链接, http: //127.0.0.1:8000/user/active/3
            # 激活链接中需要包含用户的信息,并且要把身份信息进行加密

            # 加密用户的身份信息,生成激活token
            serializer = Serializer(settings.SECRET_KEY, 3600)  # 设置过期时间为一小时
            info = {'confirm': user.id}
            token = serializer.dumps(info)  # bytes
            token = token.decode()  # 解码 默认为utf8

            # 发邮件
            # subject = '天天生鲜欢迎信息'  # 邮件标题
            # message = '邮件正文:'          # 邮件正文(有html标签则要剪贴在html_message关键字参数中)
            # sender = settings.EMAIL_FROM    # 发送人
            # receiver = [email]              # 接收人列表
            # html_message = '<h1>{},欢迎您成为天天生鲜注册会员<h1>请点击下面的链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{}">http://127.0.0.1:8000/user/active/{}</a>'.format(username,token,token)
            #
            # send_mail(subject,message ,sender, receiver,html_message=html_message)
            ''' send_mail()函数可能会发生阻塞,
                    则代码一直会停止在这: 造成用户体验差的问题

                解决问题:异步执行任务,放在后台处理--> 使用: celery包,以上发邮件代码
                转至 celery_tasks 包文件下的celery()函数处理

            '''
            # 使用celery函数发送邮件
            send_register_active_email.delay(email, username, token)
            # 任务的处理者;

            # 任务的发出者,中间人,和处理者可以在同一台电脑上启动,也可以不在同一台电脑上;

            # 返回应答
            return redirect(reverse('goods:index'))


class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密, 获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 解密和 加密时是同一个实例对象
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据用户id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# /user/login
class LoginView(View):
    '''登录'''

    def get(self, request):
        '''显示登录页面'''
        # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
        else:
            username = ''
            checked = ''
        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''进行登录校验'''
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        #业 务处理: 登录处理

        # user = authenticate(username = username, password = password)
        # user = SXuser.objects.filter(username=username).filter(password=password).first()
        try:
            user = User.objects.get(username=username)
            pwd = user.password
            # 判断密码
            if check_password(password, pwd):
                if user.is_active:
                    # 用户已激活
                    # 记录用户的登录信息(session)
                    login(request, user)
                    # 跳转至首页
                    response = redirect(reverse('goods:index'))

                    # 判断是否需要记住用户名
                    remember = request.POST.get('remember')

                    if remember == 'on':
                        # 记住用户名
                        response.set_cookie('username', username, max_age=7 * 24 * 3600)
                    else:
                        response.delete_cookie('username')

                    # 返回response
                    return response

                else:
                    # 用户未激活
                    return render(request, 'login.html', {'errmsg': '账户未激活'})
            else:
                # 用户名或密码错误
                return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '账户不存在!'})
