# -*- coding: UTF-8 -*-
'''
=================================================
@Project -> File   ：login_reg -> tasks.py
@IDE    ：PyCharm
@Author ：XuMou
@Date   ：2020/8/10 12:49
==================================================
'''
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from celery import Celery  # 导入celery包# 创建一个Celery类的实例对象

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/2')  # 使用redis数据库


# 定义任务函数
@app.task  # 装饰器，必不可少
def send_register_active_email(to_email, code):
    '''发送激活邮件'''
    '''
    这是之前没用celery进行邮件发送的 函数
    # 组织邮件信息
    # 发送邮件
    subject = "欢迎注册 XuMou'S "
    message = ''
    sender = settings.EMAIL_HOST_USER  # 发送邮件的账号
    receviver = [to_email]  # 收件人列表
    html_message = '<p>感谢注册我的博客<a href="http://{}/confirm/?code={}" target=blank>确认注册！</a></p><p>请点击链接完成注册!</p> <p>此链接有效期为{}天！</p>'.format(
        "127.0.0.1:8000", code, settings.CONFIRM_DAYS)
   
    
    '''

    # text_content是用于当HTML内容无效时的替代txt文本。
    subject = '来自XuMou项目的邮箱注册确认邮件'
    text_content = '如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'

    # subject, from_email, to = '来自XuMou的邮箱注册确认邮件', '发送邮箱@qq.com', '接受邮箱@qq.com'

    html_content = '<p>感谢注册我的博客<a href="http://{}/confirm/?code={}" target=blank>确认注册！</a></p><p>请点击链接完成注册!</p> <p>此链接有效期为{}天！</p>'.format(
        "127.0.0.1:8000", code, settings.CONFIRM_DAYS)
    print("点击的地址是celery网站〉〉", html_content)
    '''

    <p>感谢注册我的博客<a href="http://127.0.0.1:8000/confirm/?code=None" target=blank></a>,</p><p>请点击下面的链接完成注册!</p> <p>此链接有效期为1天！</p>

    '''

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
