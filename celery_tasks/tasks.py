# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
import time

# 在任务处理者一端加这几句
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "feepop_pro.settings")
django.setup()

# 创建一个Celery类的实例对象  # 第一个参数为一个任务,第二个参数是中间人
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    # 组织邮件信息
    subject = 'feepop海外购有限公司'
    message = '邮件正文:'
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>{}, 欢迎您成为Feepop注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{}">http://127.0.0.1:8000/user/active/{}</a>'.format(username, token, token)

    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)