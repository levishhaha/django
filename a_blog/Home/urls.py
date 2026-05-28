from django.urls import path
from Home.views import *

app_name = 'home'

urlpatterns = [
    path('demo',demo,name='demo'),
    path('index',index,name='index'),
    path('blog_detail/<blog_id>',blog_detail,name='blog_detail'),
    path('blog_pub',blog_pub,name='blog_pub'),
    path('pub_comment',pub_comment,name='pub_comment'),
    path('blog_image_pub',blog_image,name='blog_image'),
]
