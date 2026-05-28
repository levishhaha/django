from django.urls import path
from Buser.views import *

app_name = 'Buser'

urlpatterns = [
    path('login',Blog_login,name='login'),
    path('register',Blog_register,name='register'),
    path('captcha',send_email,name='send_email'),
    path('user',user_info,name='user_info'),
    path('logout',Blog_logout,name='Blog_logout'),
    path('blog_detail_user/<blog_id>',blog_detail_user,name='blog_detail_user')
]
