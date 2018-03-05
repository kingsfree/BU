import logging
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from collections import OrderedDict
from BU.models import *
from BU.forms import *
import random
import re


# Create your views here.
logger = logging.getLogger('BU.views')

def global_setting(request):
    SITE_NAME = settings.SITE_NAME
    # 文章归档列表
    # archive_list = Article.objects.date_distinct()
    # 标签数据
    tags = Tags.objects.all()[:20]
    # 分类数据
    # categories = Category.objects.all()
    # 近期文章数据
    recent_articles = Article.objects.all()[:10]
    return locals()

def getPage(request, articles, num):
    paginator = Paginator(articles, num)
    try:
        page = int(request.GET.get('page', 1))
        articles = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        articles = paginator.page(1)
    return articles

def getCategory(request, articles):
    category_list = []
    for article in articles:
        category = article.category.name
        if category not in category_list:
            category_list.append(category)
    return category_list

def getTags(request, articles):
    tag_list = []
    for article in articles:
        tags = article.tags.all()
        for tag in tags:
            if tag.name not in tag_list:
                tag_list.append(tag.name)
    return tag_list[:25]

def getArchive(request, articles):
    archive_list = []
    for article in articles:
        date_pre = article.date_publish
        date = date_pre.strftime('%Y年%m月文章归档')
        if date not in archive_list:
            archive_list.append(date)
    return archive_list[:10]

def index(request):
    try:
        article_js = Article.objects.filter(menu_category__name='技术')[:8]
        article_xm = Article.objects.filter(menu_category__name='项目')[:8]
        article_sh = Article.objects.filter(menu_category__name='生活')[:8]
        article_sq = Article.objects.filter(menu_category__name='社区')[:8]
    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())

def article_list(request):
    try:
        # 文章信息获取
        articles = Article.objects.filter(menu_category__name='技术')
        menu = request.GET.get('menu_name', None)
        menu_name = '技术'
        # 分页
        pages = getPage(request, articles, 4)
        archive_list = getArchive(request, articles)

        #最新文章排名

        # 分类数据
        category_list = getCategory(request, articles)
        # 标签数据
        tag_list = getTags(request, articles)


    except Exception as e:
        logger.error(e)
    return render(request, 'article_list.html', locals())


def tree_search(comment_dic, comment_obj):
    # 在comment_dic中一个一个的寻找其回复的评论
    # 检查当前评论的 reply_id 和 comment_dic中已有评论的nid是否相同，
    # 如果相同，表示就是回复的此信息
    #   如果不同，则需要去 comment_dic 的所有子元素中寻找，一直找，如果一系列中未找，则继续向下找
    for k, v_dic in comment_dic.items():
        # 找回复的评论，将自己添加到其对应的字典中，例如： {评论一： {回复一：{},回复二：{}}}
        if k == comment_obj.pid:
            comment_dic[k][comment_obj] = OrderedDict()
            return
        else:
            # 在当前第一个跟元素中递归的去寻找父亲
            tree_search(comment_dic[k], comment_obj)


def build_tree(comment_list):
    comment_dic = OrderedDict()

    for comment_obj in comment_list:
        if comment_obj.pid is None:
            # 如果是根评论，添加到comment_dic[评论对象] ＝ {}
            comment_dic[comment_obj] = OrderedDict()
        else:
            # 如果是回复的评论，则需要在 comment_dic 中找到其回复的评论
            tree_search(comment_dic, comment_obj)
    return comment_dic

def article(request):
    try:
        # 获取文章id
        id = request.GET.get('id')
        try:
            # 获取文章信息
            article = Article.objects.get(pk=id)
            article.increase_views()

        except Article.DoesNotExist:
            return render(request, 'failure.html', locals())

        # 获取点赞信息
        if request.user.is_authenticated:
            user = request.user
            likes_user_list = [like.user for like in Likes.objects.filter(article_id=id)]
            if user in likes_user_list:
                status = 1
            else:
                status = 0
        print('************before commment*****************')
        print('request.user.username:', request.user.username)
        print('request.user.is_authenticated()', request.user.is_authenticated)
        print('article-id', id)
        print('************************************')
        # 获取评论表单
        comment_form = CommentForm({
            'user': request.user.username,
            'article_id': id, } if request.user.is_authenticated else {'article_id': id})
        print('**********AAA*************')
        print(comment_form)
        # 获取评论信息
        comments = Comments.objects.filter(article__pk=id).order_by('id')
        print('************BBBB*************')
        print(comments)
        comment_dict = build_tree(comments)
        print('************CCCC*************')
        print(comment_dict)

    except Exception as e:
        print(e)
        logger.error(e)
    return render(request, 'article.html', locals())

# 提交评论
def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            #获取表单信息
            comment = Comments.objects.create(content=comment_form.cleaned_data["content"],
                                              pid=comment_form.cleaned_data['pid'],
                                              article=comment_form.cleaned_data["article"],
                                              user=request.user if request.user.is_authenticated else None)
            comment.save()
        else:
            return render(request, 'failure.html')
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

def project(request):
    try:
        articles = Article.objects.filter(menu_category__name='项目')
        menu_name = '项目'
        # 分页
        pages = getPage(request, articles, 4)
        # 分类数据
        category_list = getCategory(request, articles)
        # 标签数据
        tag_list = getTags(request, articles)
        # 文章归档列表
        archive_list = getArchive(request, articles)

    except Exception as e:
        logger.error(e)
    return render(request, 'project.html', locals())

def life(request):
    try:
        articles = Article.objects.filter(menu_category__name='生活')
        menu_name = '生活'
        # 分页
        pages = getPage(request, articles, 4)
        # 分类数据
        category_list = getCategory(request, articles)
        # 标签数据
        tag_list = getTags(request, articles)
        # 文章归档列表
        archive_list = getArchive(request, articles)

    except Exception as e:
        logger.error(e)
    return render(request, 'life.html', locals())

def getusers(articles):
    userlist = [article.author.username for article in articles]
    userlist2 = list(set(userlist))
    userdict = {}
    for user in userlist2:
        userdict[user] = userlist.count(user)
    userlist3 = sorted(userdict.items(), key=lambda item: item[1], reverse=True)
    usernames = [item[0] for item in userlist3[:10]]
    users = [MyUser.objects.filter(username=item)[0] for item in usernames]
    return users

def topics(request):
    try:
        articles = Article.objects.filter(menu_category__name='社区')
        # 用户活跃度排名
        users_list = getusers(articles)
        menu_name = '社区'
        # 分页
        pages = getPage(request, articles, 5)
        # 标签数据
        tag_list = getTags(request, articles)

    except Exception as e:
        logger.error(e)
    return render(request, 'topics.html', locals())

def archive(request):
    try:
        #先获取客户端提交的信息
        year = request.GET.get('year', None)
        month = request.GET.get('month', None)
        menu_name = request.GET.get('menu_name', None)
        articles = Article.objects.filter(menu_category__name=menu_name).filter(date_publish__icontains=year + '-' + month)
        # 分页
        pages = getPage(request, articles, 4)
        # 分类数据
        category_list = getCategory(request, articles)
        # 标签数据
        tag_list = getTags(request, articles)

    except Exception as e:
        logger.error(e)
    return render(request, 'archive.html', locals())

def category(request):
    try:
        category = request.GET.get('category', None)
        menu_name = request.GET.get('menu_name', None)
        articles = Article.objects.filter(menu_category__name=menu_name).filter(category__name__icontains=category)
        # 文章归档列表
        archive_list = getArchive(request, articles)
        # 分页
        pages = getPage(request, articles, 4)
        # 标签数据
        tag_list = getTags(request, articles)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())

def tagPage(request):
    try:
        tag = request.GET.get('tag', None)
        menu_name = request.GET.get('menu_name', None)
        articles = Article.objects.filter(menu_category__name=menu_name).filter(tags__name__icontains=tag)
        # 文章归档列表
        archive_list = getArchive(request, articles)
        # 分页
        pages = getPage(request, articles, 4)
        # 分类数据
        category_list = getCategory(request, articles)
    except Exception as e:
        logger.error(e)
    return render(request, 'tagpage.html', locals())


@csrf_exempt
def ajax_signup(request):
    try:
        if request.method == 'POST' and request.POST:
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = MyUser.objects.create(username=reg_form.cleaned_data["username"],
                                             email=reg_form.cleaned_data["email"],
                                             password=make_password(reg_form.cleaned_data["password"]), )
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                login(request, user)
                data = {"status": 1}
                return JsonResponse(data)
            else:
                error_messages = {}
                for field in reg_form.errors:
                    error_messages[field]=reg_form.errors[field][0]
                print(error_messages)
                data = {
                    'status': 0,
                    'error_messages': error_messages
                }
                return JsonResponse(data)
        else:
            return render(request, 'failure.html', locals())
    except Exception as e:
        logger.error(e)


@csrf_exempt
def ajax_login(request):
    try:
        if request.method == 'POST' and request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data["email"]
                username = MyUser.objects.filter(email=email)[0].username
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                    login(request, user)
                    response_data = {
                        "status": 1
                    }
                    return JsonResponse(response_data)
                else:
                    response_data = {
                        "status": 0,
                        "error_messages": 1
                    }
                    return JsonResponse(response_data)

            else:
                error_messages = {}
                for field in login_form.errors:
                    error_messages[field] = login_form.errors[field][0]
                response_data = {
                    "status": 0,
                    'error_messages': error_messages
                }
                return JsonResponse(response_data)
        else:
            login_form = LoginForm()

    except Exception as e:
        logger.error(e)

# 注销
@login_required
def do_logout(request):
    try:
        logout(request)
        return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        logger.error(e)

def generate_verification_code():
    code_list = []
    for i in range(2):
        num1 = random.randint(0, 9)  # 数字0-9
        num2 = random.randint(65, 90)  # 字母A-Z的ascii码值
        num3 = random.randint(97, 122)  # 字母a-z的ascii码值
        code_list.append(str(num1))
        code_list.append(chr(num2))
        code_list.append(chr(num3))
    verify_code = ''.join(code_list)
    return verify_code

@csrf_exempt
def ajax_email(request):
    try:
        if request.method == 'POST' and request.POST:
            email_form = EmailSendForm(request.POST)
            if email_form.is_valid():
                email = email_form.cleaned_data['email']
                username = MyUser.objects.filter(email=email)[0].username
                code = generate_verification_code()
                subject = '你此次重置密码的验证码是{}'.format(code)
                message = '{}, 你好, 你此次重置密码的验证码是 {}, 请输入验证码进行下一步操作。 如非你本人操作，请忽略此邮件。————来自BU'.format(username, code)
                try:
                    send_mail(
                        subject,
                        message,
                        'beuweb@163.com',
                        [email],
                    )
                    data = {
                        'status': '1',
                        'code': code,
                        'email': email
                    }
                    return JsonResponse(data)
                except BadHeaderError:
                    data = {
                        'status': 0,
                        'error_messages': 1
                    }
                    return JsonResponse(data)
            else:
                error_messages = {}
                for field in email_form.errors:
                    error_messages[field] = email_form.errors[field][0]
                data = {
                    'status': 0,
                    'error_messages': error_messages
                }
                return JsonResponse(data)
        else:
            email_form = EmailSendForm()

    except Exception as e:
        logger.error(e)

@csrf_exempt
def reset_password(request):
    try:
        if request.method == 'POST' and request.POST:
            reset_password_form = ResetPasswordForm(request.POST)
            if reset_password_form.is_valid():
                raw_code = reset_password_form.cleaned_data['raw_code']
                code = reset_password_form.cleaned_data['code']
                if code == raw_code:
                    email = reset_password_form.cleaned_data['email']
                    username = MyUser.objects.filter(email=email)[0].username
                    new_password = reset_password_form.cleaned_data['password']
                    user = MyUser.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    user = authenticate(username=username, password=new_password)
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                    login(request, user)
                    response_data = {
                        "status": 1
                    }
                    return JsonResponse(response_data)
                else:
                    response_data = {
                        "status": 0,
                        "error_messages": 1
                    }
                    return JsonResponse(response_data)
            else:
                error_messages = {}
                for field in reset_password_form.errors:
                    error_messages[field] = reset_password_form.errors[field][0]
                data = {
                    'status': 0,
                    'error_messages': error_messages
                }
                return JsonResponse(data)
        else:
            reset_password_form = ResetPasswordForm()
    except Exception as e:
        logger.error(e)

@login_required
@csrf_exempt
def likes_set(request):
    try:
        if request.method == 'POST' and request.POST:
            username = request.POST['username']
            article_id = request.POST['article_id']
            likes_num = request.POST['likes_num']
            user = MyUser.objects.get(username=username)
            article_id_list = [like.article_id for like in  Likes.objects.filter(user=user)]
            if int(article_id) in article_id_list:
                Likes.objects.get(article_id=article_id, user=user).delete()
                likes_num = int(likes_num) - 1
                if likes_num < 0:
                    likes_num = 0
                data = {
                    'likes_num': likes_num,
                    'status': 0
                }
                return JsonResponse(data)
            else:
                Likes.objects.create(article_id=article_id, user=user)
                likes_num = int(likes_num) + 1
                data = {
                    'likes_num': likes_num,
                    'status': 1
                }
                return JsonResponse(data)
        else:
            return render(request, 'failure.html')
    except Exception as e:
        logger.error(e)


@login_required
@csrf_exempt
def avatar_upload(request):
    try:
        if request.method == 'POST' and request.POST:
            username = request.POST.get('username')
            img = request.FILES.get('img')
            request.user.avatar = img
            request.user.save()
            user = MyUser.objects.get(username=username)
            avatar = user.avatar
            data = {
                'status': 1,
                'avatar': avatar.url
            }
            return JsonResponse(data)
        else:
            return render(request, 'failure.html')
    except Exception as e:
        logger.error(e)


def article_publicate(request):
    try:
        if request.method == 'POST' and request.POST:
            article_pubform = ArticlePubForm(request.POST, request.FILES)
            if article_pubform.is_valid():
                article = Article.objects.create(
                    title=article_pubform.cleaned_data['title'],
                    description=article_pubform.cleaned_data['description'],
                    content=article_pubform.cleaned_data['content'],
                    photo=article_pubform.cleaned_data['photo'],
                    menu_category_id=4,
                    author=request.user,
                    category_id=4,
                )
                tags = re.split(',|，', article_pubform.cleaned_data['tagstext'])
                for tag in tags:
                    tag_obj = Tags.objects.filter(name=tag)
                    if tag_obj:
                        article.tags.add(tag_obj[0])
                    else:
                        tag_obj = Tags.objects.create(name=tag)
                        article.tags.add(tag_obj)
                article.save()
                return HttpResponseRedirect('/topics?menu_name=sq')
            else:
                return render(request, 'article_publicate.html', locals())
        else:
            article_pubform = ArticlePubForm()
            return render(request, 'article_publicate.html', locals())
    except Exception as e:
        logger.error(e)
    return render(request, 'article_publicate.html', locals())


def userinfo(request):
    try:
        username = request.user.username
        articles = Article.objects.filter(author__username=username)
        pages = getPage(request, articles, 5)
        # 标签数据
        tag_list = getTags(request, articles)
    except Exception as e:
        logger.error(e)
    return render(request, 'userinfo.html', locals())


def articleDelete(request):
    try:
        if request.method == 'GET' and request.GET:
            article_id = request.GET.get('article_id')
            article = Article.objects.get(pk=article_id)
            article.delete()
            data = {
                "status": 1
            }
            return JsonResponse(data)
        else:
            return render(request, 'failure.html')
    except Exception as e:
        logger.error(e)
    return render(request, 'userinfo.html', locals())

def articleEdit(request):
    try:
        if request.method == 'POST' and request.POST:
            article_editform = ArticleEditForm(request.POST, request.FILES)
            if article_editform.is_valid():
                title = article_editform.cleaned_data['title']
                description = article_editform.cleaned_data['description']
                content = article_editform.cleaned_data['content']
                article_id = article_editform.cleaned_data['article_id']
                photo = article_editform.cleaned_data['photo']
                article = Article.objects.get(pk=article_id)
                article.title = title
                article.description = description
                article.content = content
                if photo != 'default.png':
                    article.photo = photo
                tags_raw = re.split(',|，', article_editform.cleaned_data['tagstext'])
                tags = []
                for tag in tags_raw:
                    tags.append(tag.split()[0])
                article.tags.clear()
                for tag in tags:
                    tag_obj = Tags.objects.filter(name=tag)
                    if tag_obj:
                        article.tags.add(tag_obj[0])
                    else:
                        tag_obj = Tags.objects.create(name=tag)
                        article.tags.add(tag_obj)
                article.save()
                return HttpResponseRedirect('/topics?menu_name=sq')
            else:
                return render(request, 'article_edit.html', locals())
        else:
            article_id = request.GET.get('articleid')
            article = Article.objects.get(pk=article_id)
            tags = article.tags.all()
            tagtext = ''
            for tag in tags:
                tagtext = tag.name + ', ' + tagtext
            tagstext = tagtext.rsplit(',', 1)[0]
            article_editform = ArticleEditForm(initial={
                'title': article.title,
                'description': article.description,
                'content': article.content,
                'photo': article.photo,
                'tagstext': tagstext,
                'article_id': article_id
            })
            return render(request, 'article_edit.html', locals())
    except Exception as e:
        logger.error(e)
    return render(request, 'article_edit.html', locals())

def search(request):
    try:
        if request.method == 'GET' and request.GET:
            keywords = request.GET.get('keywords')
            if keywords:
                articles = Article.objects.filter(title__icontains=keywords)
                articles_list = []
                article_list = {}
                for article in articles:
                    article_list['title'] = article.title
                    article_list['id'] = article.id
                    articles_list.append(article_list)
                    article_list = {}
                data = {
                    'status': 1,
                    'articles': articles_list[:15],
                }
                return JsonResponse(data)
            else:
                data = {
                    'status': 0
                }
                return JsonResponse(data)
        else:
            return render(request, 'failure.html')
    except Exception as e:
        logger.error(e)

def resultpage(request):
    try:
        keyword = request.GET.get('keywords')
        articles = Article.objects.filter(title__icontains=keyword)
        # 分页
        pages = getPage(request, articles, 4)
    except Exception as e:
        logger.error(e)
    return render(request, 'search_result.html', locals())
