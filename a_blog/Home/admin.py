from django.contrib import admin
from .models import Blog,Comment

# Register your models here.

# 博客字段
class BlogAdmin(admin.ModelAdmin):
    # 指定在后台管理端的列表页面显示的字段
    list_display = ['title','content','pub_time','author']

# 评论字段
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['blog','content','pub_time','author']

# 将上述模型注册到django管理后台
admin.site.register(Blog,BlogAdmin)
admin.site.register(Comment,BlogCommentAdmin)
