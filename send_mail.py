# -*- coding: UTF-8 -*-
'''
=================================================
@Project -> File   ：login_reg -> send_mail.py.py
@IDE    ：PyCharm
@Author ：XuMou
@Date   ：2020/7/29 22:38
==================================================
'''

import os
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'login_reg.settings'

if __name__ == '__main__':

    # send_mail(
    #     '来自XuMou的测试邮件',
    #     '我在进行django小项目的总结',
    #     '2745254260@qq.com',
    #     ['1187188906@qq.com'],
    # )
    '''
    text_content是用于当HTML内容无效时的替代txt文本。
    '''
    subject, from_email, to = '来自XuMou的测试html邮件', '2745254260@qq.com', '1187188906@qq.com'
    text_content = '欢迎访问我的博客www.baidu.com'
    html_content = '<p>欢迎访问<a href="http://www.baidu.com" target=blank>www.baidu.com</a></p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()