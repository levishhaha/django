from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods,require_POST
from .models import Blog,Comment
from .forms import PubBlogForm
from django.http.response import JsonResponse
from django.core.paginator import Paginator
import os
from uuid import uuid4  # 避免文件名重复
from django.conf import settings
from django.utils.html import strip_tags # 用来处理博客的标签方便表单处理
import ollama # 导入模型调用库
import threading
from django.db.models import Q, Case, When, IntegerField

# Create your views here.

def demo(request):
    return HttpResponse('链接成功')

#首页
@require_http_methods(['GET','POST'])
def index(request):
    if request.method == 'GET':
        # 按时间倒序获取博客数据
        blog_list = Blog.objects.all().order_by('-pub_time')
        # 分页器将数据分页
        paginator = Paginator(blog_list,per_page=20)
        # 获取前端传入的页数，如果没有，默认为1
        page_num = request.GET.get('page',1)
        # 获得该页数的数据
        page_obj = paginator.get_page(page_num)

        if request.user.is_authenticated:
            username = request.user.username
            email = request.user.email
            # print(username,email)
            context = {
                'username': username,
                'email': email,
                'blog': page_obj,
                # 传入分页器对象，用来做页码导航
                'paginator': paginator
            }
            return render(request,'index.html',context)
        else:
            context = {
                'blog': page_obj,
                'paginator': paginator
            }
            return render(request,'index.html',context)
    else:
        search = request.POST.get('search').strip() # 去除空格
        blog_list = Blog.objects.all().order_by('-pub_time')

        #  搜索内容 
        if search:
            # 找出所有匹配的数据
            blog_list = blog_list.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
            # 分别给每个字段打分，再相加
            blog_list = blog_list.annotate(
                total_score = (
                    # 标题得分
                    Case(When(title__icontains=search, then=10), default=0, output_field=IntegerField())
                    # 简介得分
                    +Case(When(content__icontains=search, then=5), default=0, output_field=IntegerField())
                    # 内容得分
                    +Case(When(tags__icontains=search, then=2), default=0, output_field=IntegerField())
                )
            ).order_by("-total_score", "-pub_time")


        # 分页器将数据分页
        paginator = Paginator(blog_list,per_page=20)
        # 获取前端传入的页数，如果没有，默认为1
        page_num = request.GET.get('page',1)
        # 获得该页数的数据
        page_obj = paginator.get_page(page_num)

        if request.user.is_authenticated:
            username = request.user.username
            email = request.user.email
            # print(username,email)
            context = {
                'username': username,
                'email': email,
                'blog': page_obj,
                # 传入分页器对象，用来做页码导航
                'paginator': paginator
            }
            return render(request,'index.html',context)
        else:
            context = {
                'blog': page_obj,
                'paginator': paginator
            }
            return render(request,'index.html',context)
        


def blog_detail(request,blog_id):
    try:
        # 从数据库中获去指定id的博客对象
        blog = Blog.objects.get(pk=blog_id) # pk表示主键
    except Exception as e:
        blog = None
    return render(request,'blog_detail.html',context={'blog': blog})


@require_http_methods(['GET','POST'])
def blog_pub(request):
    if request.user.is_authenticated:
        if request.method=='GET':
            return render(request,'blog_pub.html')
        else:
            # 复制一份提交参数
            data = request.POST.copy()
            # 去除所有标签
            data['content'] = strip_tags(data.get('content',''))
            form = PubBlogForm(data=data)
            if form.is_valid():
                title = form.cleaned_data.get('title')
                content = request.POST.get('content')
                blog = Blog.objects.create(title=title,content=content,author=request.user)

                # 将博客内容及id发送给ai进行打标签
                try:
                    data = {
                        'text': content,
                        'blog_id': blog.id
                    }
                    t = threading.Thread(target=ollama_get_tags,args=(data,))
                    t.daemon = False
                    t.start()
                except Exception:
                    pass

                # 返回博客保存信息
                return JsonResponse({'code': 200,'message': '成功发布','data': {'blog_id': blog.id}})
            else:
                for errors_a in form.errors.get_json_data().values():
                    error_a = errors_a[0]['message']
                    # print(error_a)
                    break
                return JsonResponse({'code': 400,'message': error_a})
    else:
        return redirect(reverse('Buser:login'))


@require_POST
def pub_comment(request):
    if request.user.is_authenticated:
        blog_id = request.POST.get('blog_id')
        content = request.POST.get('content')
        if content == '':
            return redirect(reverse('home:blog_detail',kwargs={'blog_id': blog_id}))
        else:
            Comment.objects.create(content=content,blog_id=blog_id,author=request.user)
            return redirect(reverse('home:blog_detail',kwargs={'blog_id': blog_id}))
    else:
        return redirect(reverse('Buser:login'))
    

# 图片上传接口
@require_http_methods(['POST'])
def blog_image(request):
    if request.user.is_authenticated:
        # print('处理上传数据')
        # 只处理POST请求
        if request.method != "POST":
            # print('请求错啦！')
            return JsonResponse({"errno": 1, "message": "请求错啦！"})
        
        # 1. 接收上传的文件（默认字段名是 'file'，和编辑器配置一致
        file_obj = request.FILES.get("file")
        if not file_obj:
            # print('没有上传文件')
            return JsonResponse({"errno": 1, "message": "没有上传文件"})
        
        # 2. 校验文件类型（只允许图片）
        if not file_obj.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            # print('不支持的文件类型')
            return JsonResponse({"errno": 1, "message": "不支持的文件类型"})
        
        # 3. 生成唯一文件名，防止覆盖
        ext = file_obj.name.split('.')[-1]
        new_filename = f"{uuid4().hex}.{ext}"
        # print('生成了唯一文件名',new_filename)

        # 4. 保存到 media 目录下的 uploads/blog_image 文件夹
        save_dir = os.path.join(settings.MEDIA_ROOT, "uploads/blog_image")
        os.makedirs(save_dir, exist_ok=True)  # 文件夹不存在则创建
        save_path = os.path.join(save_dir, new_filename)
        # print('保存到该目录下？')

        # 写入文件
        with open(save_path, "wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
            # print('写进去了？')

        image_url = f"{settings.MEDIA_URL}uploads/blog_image/{new_filename}"

        return JsonResponse({
            "errno": 0,
            "data": {
                "url": image_url
            }
        })

    else:
        JsonResponse({"errno": 1, "message": "没登录，你在干嘛呢！"})



# 获取标签的函数,不做路由
def ollama_get_tags(data):
    text = data.get('text')
    blog_id = data.get('blog_id')
    if not text.strip():
        return 0
    # 去除所有html标签
    text = strip_tags(text)
    prompt = f"请根据下面文本，提炼出1到3个能概括内容的中文标签,标签之间用逗号分隔,内容如下:{text}"
    try:
        res = ollama.generate(
            #去settings里面读取你写的模型名称
            model=settings.OLLAMA_MODEL,
            #发给大模型的提问文案
            prompt=prompt,
            #随机性参数 数值越低回答越规整统一
            options={"temperature": 0.5}
        )

        # 将标签保存到数据库
        blog = Blog.objects.get(id=blog_id)
        blog.tags = res["response"].strip().replace("，", ",")
        blog.save()

        #获取ai返回的回答，去掉空格，把中文逗号全部换成英文逗号
        # print(res["response"])
        return 1
    #如果模型报错、卡顿、未启动，捕获错误，不会让网站崩溃
    except Exception as e:
        print(e)
        return 0
