from django.db import models
from django.contrib.auth import get_user_model # 导入用户模型

# Create your models here.
User = get_user_model()

# 博客
class Blog(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    # 关联用户
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    # 标签，非必填
    tags = models.CharField(null=True,blank=True,max_length=100)

    # 定义模型原数据：用于配置模型的行为和显示方式，不会影响数据库的结构
    class Meta:
        # 指定模型在django管理后台中显示的名称
        verbose_name = '博客'
        verbose_name_plural = verbose_name

# 评论
class Comment(models.Model):
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    # 关联博客                                              允许关联的对象反向查询
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='contents',verbose_name='评论')
    # 关联用户
    author = models.ForeignKey(User,on_delete=models.CASCADE)

    # 定义模型原数据：用于配置模型的行为和显示方式，不会影响数据库的结构
    class Meta:
        # 指定模型在django管理后台中显示的名称
        verbose_name = '评论'
        verbose_name_plural = verbose_name