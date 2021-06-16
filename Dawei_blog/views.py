from django.shortcuts import render,redirect
from .models import BlogPost
from django.http import HttpResponse
from .forms import BlogPostForm
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.decorators import login_required
import markdown
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
# Create your views here.
#from django.http import HttpResponse

# 视图函数

#显示所有blog在同一页面
def blog_list(request):
    # 取出所有博客文章
    blogs = BlogPost.objects.all()
    # 需要传递给模板（templates）的对象
    context = {'blogs': blogs}
    # render函数：载入模板，并返回context对象
    return render(request, 'blog/list.html', context)

def blog_detail(request, id):
    # 取出相应的文章
    blog = BlogPost.objects.get(id=id)

    # 浏览量 +1
    blog.total_views += 1
    blog.save(update_fields=['total_views'])
    # 取出文章评论
    comments = Comment.objects.filter(blog=id)

    md = markdown.Markdown(
            extensions=[
        # 包含 缩写、表格等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        # 目录扩展
        'markdown.extensions.toc',
        ])
    # 需要传递给模板的对象
    blog.body = md.convert(blog.body)

    # 新增了md.toc对象
    context = {'blog': blog, 'toc': md.toc, 'comments': comments}
    # 载入模板，并返回context对象
    return render(request, 'blog/detail.html', context)

# 写文章的视图, 检查登录
@login_required(login_url='/userprofile/login/')
def blog_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        blog_post_form = BlogPostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if blog_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_blog = blog_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_blog.author = User.objects.get(id=request.user.id)#!!!!
            # 将新文章保存到数据库中
            new_blog.save()
            # 完成后返回到文章列表
            return redirect("Dawei_blog:blog_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        blog_post_form = BlogPostForm()

        # 赋值上下文
        context = { 'blog_post_form': blog_post_form }
        # 返回模板
        return render(request, 'blog/create.html', context)


# 删文章
@login_required(login_url='/userprofile/login/')
def blog_safe_delete(request, id):
    # 根据 id 状态获取需要删除的文章
    blog = BlogPost.objects.get(id=id)
    if request.user != blog.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    elif request.method == 'POST':
        blog = BlogPost.objects.get(id=id)
        # 调用.delete()方法删除文章
        blog.delete()
    # 完成删除后返回文章列表
        return redirect("Dawei_blog:blog_list")
    else:
        return HttpResponse("无权限删除此文章")


# 更新文章
@login_required(login_url='/userprofile/login/')
def blog_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    blog = BlogPost.objects.get(id=id)
    if request.user != blog.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        blog_post_form = BlogPostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if blog_post_form.is_valid() :
            # 保存新写入的 title、body 数据并保存
            blog.title = request.POST['title']
            blog.body = request.POST['body']
            blog.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("Dawei_blog:blog_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        blog_post_form = BlogPostForm()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = { 'blog': blog, 'blog_post_form': blog_post_form }
        # 将响应返回到模板中
        return render(request, 'blog/update.html', context)


# 引入分页模块
def blogs_list(request):
    # 修改变量名称（articles -> article_list）
    search = request.GET.get('search')
    order = request.GET.get('order')

    if search:
        if order == 'total_views':
            # 用 Q对象 进行联合搜索
            blog_list = BlogPost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            blog_list = BlogPost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        # 将 search 参数重置为空
        search = ''
        if order == 'total_views':
            blog_list = BlogPost.objects.all().order_by('-total_views')
        else:
            blog_list = BlogPost.objects.all()
            order = 'normal'


    # 每页显示 10 篇文章
    paginator = Paginator(blog_list, 10)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 blogs
    blogs = paginator.get_page(page)
    #context 引入order,search
    context = { 'blogs': blogs, 'order': order, 'search': search}

    return render(request, 'blog/list.html', context)


