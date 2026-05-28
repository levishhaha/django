from django.db import models
from django.contrib.auth.models import User
import os
import uuid
# Create your models here.
def rename_avatar(instance, filename):
    # 截取文件后缀
    suffix = os.path.splitext(filename)[1]
    # 自定义新文件名：用户ID+随机串
    new_filename = f"avatar_{instance.user.id}_{uuid.uuid4()}{suffix}"
    return os.path.join("avatars", new_filename)

class UserInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    #头像存放 avatars文件夹
    avatar = models.ImageField(upload_to=rename_avatar,default='avatars/default.png')