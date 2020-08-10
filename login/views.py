from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect

# Create your views here.
# from login_reg import settings
from django.conf import settings
from .models import *
from . import forms

import datetime
from .models  import ConfirmString
from django.core.mail import EmailMultiAlternatives

# 用户密码加密
import hashlib


def index(request):
    if not request.session.get("is_login", None):
        return redirect('/login/')
    return render(request, 'index.html')


def login(request):
    if request.session.get("is_login", None):  # 不允许重复登录
        return redirect('/index/')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = User.objects.get(name=username)
            except:
                message = "用户不存在!"
                return render(request, 'login.html', locals())

            if not user.has_confirmed:
                message = '该用户还未经过邮件确认！'
                return render(request, 'login.html', locals())

            if user.password == hash_code(password):
                request.session["is_login"] = True
                request.session["user_id"] = user.id
                request.session["username"] = user.name
                print(username, password)
                return redirect('/index/')
            else:
                message = '密码不正确'
                return render(request, "login.html", locals())

        else:
            return render(request, 'login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)  # 确认
                print("确认码为〉〉",code)

                # send_email(email, code)
                # 使用celery进行异步发送注册确认确认
                from celery_tasks.tasks import send_register_active_email  # 导入celery发邮件的方法
                send_register_active_email(email,code)
                message = '请前往邮箱进行确认！'
                return render(request, 'confirm.html', locals())
        else:
            return render(request, 'register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()  # flush 一次性将session中的所有内容全部清空
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/login/')


def hash_code(s, salt="login_reg"):  # 加盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 创建确认码对象
'''
make_confirm_string()方法接收一个用户对象作为参数。首先利用datetime模块生成一个当前时间的字符串now，
再调用我们前面编写的hash_code()方法以用户名为基础，now为‘盐’，生成一个独一无二的哈希值，
再调用ConfirmString模型的create()方法，生成并保存一个确认码对象。最后返回这个哈希值
'''


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    ConfirmString.objects.create(code=code, user=user)
    return code



def send_email(email,code):
    '''
    text_content是用于当HTML内容无效时的替代txt文本。
    '''

    subject = '来自XuMou项目的邮箱注册确认邮件'
    text_content = '如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'


    # subject, from_email, to = '来自XuMou的邮箱注册确认邮件', '发送邮箱@qq.com', '接受邮箱@qq.com'

    html_content = '<p>感谢注册我的博客<a href="http://{}/confirm/?code={}" target=blank>确认注册！</a></p><p>请点击链接完成注册!</p> <p>此链接有效期为{}天！</p>'.format("127.0.0.1:8000",code,settings.CONFIRM_DAYS)
    print("点击的〉〉",html_content)
    '''
    
    <p>感谢注册我的博客<a href="http://127.0.0.1:8000/confirm/?code=None" target=blank></a>,</p><p>请点击下面的链接完成注册!</p> <p>此链接有效期为1天！</p>
    
    '''

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# 邮件确认函数
def user_confirm(request):
    '''

        通过request.GET.get('code', None)从请求的url地址中获取确认码;
        先去数据库内查询是否有对应的确认码;
        如果没有，返回confirm.html页面，并提示;
        如果有，获取注册的时间c_time，加上设置的过期天数，这里是7天，然后与现在时间点进行对比；
        如果时间已经超期，删除注册的用户，同时注册码也会一并删除，然后返回confirm.html页面，并提示;
        如果未超期，修改用户的has_confirmed字段为True，并保存，表示通过确认了。然后删除注册码，但不删除用户本身。最后返回confirm.html页面，并提示。

    '''
    code=request.GET.get('code',None)
    message=''
    try:
        confirm=ConfirmString.objects.get(code=code)
    except:
        message="无效的确认请求"
        return render(request,'confirm.html',locals())
    c_time=confirm.c_time
    now=datetime.datetime.now()
    if now > c_time+datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'confirm.html', locals())



