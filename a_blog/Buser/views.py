from django.shortcuts import render,redirect
from django.http.response import JsonResponse
from django.core.mail import send_mail # 验证码发送
import random
from django.core.cache import cache   # 导入缓存模块
from django.views.decorators.http import require_http_methods,require_POST
from .forms import RegisterForm,LoginForm
from django.contrib.auth import get_user_model,login,logout
from django.urls import reverse
from .models import UserInfo
from Home.models import Blog
from django.core.paginator import Paginator


User = get_user_model()

# Create your views here.

@require_http_methods(['GET','POST'])
def Blog_login(request):
    if request.method=='GET':
        return render(request,'login.html')
    else:
        form = LoginForm(request.POST)
        # test_a = request.POST.get('remember')
        # print(test_a)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            # print(remember)
            # 根据邮箱进行查找
            user = User.objects.filter(email=email).first()
            # 再判断对应的密码是否匹配
            if user and user.check_password(password):
                # 调用login函数(注意函数名不要重复)
                login(request,user)
                # 用户已经通过身份验证
                user.is_authenticated
                # 判断是否要记住我
                if not remember:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(7*24*3600)
                return JsonResponse({'code': 200,'message': '登录成功'})
            else:
                return JsonResponse({'code': 400,'message': '账号或密码错误'})
        else:
            # print('账号密码是空的吗')
            for errors_a in form.errors.get_json_data().values():
                error_a = errors_a[0]['message']
                # print(error_a)
                break
            return JsonResponse({'code': 400,'message': error_a})


@require_http_methods(['GET','POST'])
def Blog_register(request):
    if request.method=='GET':
        return render(request,'register.html')
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 验证验证码是否正确
            # print('验证验证码是否正确')
            capt = request.POST.get('captcha')
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # print(type(cache.get(f'captcha_{email}')),type(capt))
            try:
                if int(capt) == cache.get(f'captcha_{email}'):
                    # print('验证码正确了?')
                    # print(capt)
                    exists_1 = User.objects.filter(username=username).exists()
                    if exists_1:
                        return JsonResponse({'code': 400,'message': '昵称已被使用'})
                    exists = User.objects.filter(email=email).exists()
                    if exists:
                        return JsonResponse({'code': 400,'message': '邮箱已被注册'})
                    # 相比于create()方法,create_user()会加密处理，更安全
                    user = User.objects.create_user(email=email,username=username,password=password)
                    UserInfo.objects.create(user=user)
                    return JsonResponse({'code': 200,'message': '注册成功，请前往登陆页面登录'})
                else:
                    return JsonResponse({'code': 400,'message': '验证码错误'})
            # 没有输入验证码
            except:
                return JsonResponse({'code': 400,'message': '请输入验证码'})
        else:
            # print('总不能都没有数据提交吧')
            # print(form.errors.get_json_data().items)
            for errors_a in form.errors.get_json_data().values():
                error_a = errors_a[0]['message']
                # print(error_a)
                break
            return JsonResponse({'code': 400,'message': error_a})


# 邮箱验证码发送
def send_email(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'code': 400,'message': '邮箱错误，请重新输入'})
    # 随机生成六位数验证码
    capt = random.randint(100000,999999)
    # 将验证码存入缓存中
    cache.set(f'captcha_{email}',capt,timeout=60)
    # 调用发送函数
    try:
        send_mail(
            subject='博客验证码',   # 邮件主题
            message=f'[博客]注册验证码：{capt},请勿将验证码泄露给他人，验证码有效时间为60秒。若非本人操作，请忽略本条信息。',   # 邮件内容
            recipient_list=[email],      # 收件人邮箱列表
            from_email=None    # 使用默认设置
        )
        return JsonResponse({'code': 200,'message': '验证码已发送，请注意查收'})
    except:
        return JsonResponse({'code': 400,'message': '请输入正确的邮箱'})


@require_http_methods(['GET','POST'])
def user_info(request):
    if request.user.is_authenticated:
        if request.method=='GET':
            username = request.user.username
            email = request.user.email

            # 获取用户博客数据
            blog_list = Blog.objects.filter(author_id=request.user.id).order_by('-pub_time')
            paginator = Paginator(blog_list,per_page=20)
            page_num = request.GET.get('page',1)
            page_obj = paginator.get_page(page_num)

            context = {
                'username': username,
                'email': email,
                'blog': page_obj,
                'paginator': paginator
            }
            return render(request,'user_info.html',context)
        elif request.method=='POST':
            new_username = request.POST.get('username')
            new_user_image = request.FILES.get('user_image')
            if new_username:
                user = User.objects.get(username=request.user)
                user.username = new_username
                user.save()
            if new_user_image:
                user_img = request.user.userinfo
                user_img.avatar = new_user_image
                user_img.save()
                
            return redirect(reverse('Buser:user_info'))
        else:
            return JsonResponse({'code': 400,'message': '什么鬼你在干嘛?'})
    else:
        return render(request,'user_info_unlogin.html')

# 退出登录
def Blog_logout(request):
    logout(request)
    return redirect(reverse('home:index'))



# 用户管理博客
@require_http_methods(['GET','POST'])
def blog_detail_user(request,blog_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                # 从数据库中获去指定id的博客对象
                blog = Blog.objects.get(pk=blog_id) # pk表示主键
            except Exception as e:
                blog = None
            if request.user.id == blog.author_id :
                return render(request,'blog_detail_user.html',context={'blog': blog})
            else:
                return render(request,'blog_detail_user.html')
        else:
            return redirect(reverse('Buser:user_info'))
    else:
        value = request.POST.get('type')
        if value == '1':
            blog = Blog.objects.get(pk=blog_id)
            blog.delete()
        return redirect(reverse('Buser:user_info'))
