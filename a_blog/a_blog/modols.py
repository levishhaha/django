# 还是配置用户头像
from django.db import models

class UserProfile(models.Model):
    avatar = models.ImageField(
        upload_to='avatars/',  # 文件会被自动存到 media/avatars/ 下面
        default='avatars/default.png'  # 默认头像可以放在 media/avatars/ 里
    )