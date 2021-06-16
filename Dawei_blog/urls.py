# 引入path
from django.urls import path
from . import views

# 正在部署的应用的名称
app_name = 'Dawei_blog'

urlpatterns = [

    path('blog-list/', views.blogs_list, name='blog_list'),
    path('blog-detail/<int:id>/', views.blog_detail, name='blog_detail'),
# 写文章
    path('blog-create/', views.blog_create, name='blog_create'),
    #path('blog-delete/<int:id>/', views.blog_delete, name='blog_delete'),
    path('blog-safe-delete/<int:id>/',views.blog_safe_delete,name='blog_safe_delete'),
    #更新blog
    path('blog_update/<int:id>/', views.blog_update, name = 'blog_update'),

]