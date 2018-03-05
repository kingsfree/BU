from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
import django.utils.timezone as timezone

# Create your models here.

class MyUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatar/%Y/%m/', default='avatar/default.png', max_length=200, blank=True, null=True, verbose_name='用户头像')
    qq = models.CharField(max_length=20, blank=True, null=True, verbose_name='QQ号码')
    mobile = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    age = models.IntegerField(blank=True, null=True, verbose_name='年龄',)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'myuser'

    def __str__(self):
        return self.username

class MenuCategory(models.Model):
    name = models.CharField(max_length=20, verbose_name='菜单栏类别')

    class Meta:
        verbose_name = '菜单栏类别'
        verbose_name_plural = '菜单栏类别'
        db_table = 'manu_category'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name='分类名称')
    index = models.IntegerField(default=999, verbose_name='分类排序')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        db_table = 'category'

    def __str__(self):
        return self.name

class Tags(models.Model):
    name = models.CharField(max_length=20, verbose_name='标签名称')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        db_table = 'tags'

    def __str__(self):
        return self.name

#自定义一个Article Model的管理器
# 1 增加一个数据处理方法
# 2 采用get_queryset的方法
class ArticleManager(models.Manager):
    def date_distinct(self):
        distinct_date_list = []
        date_list = self.values('date_publish')
        for date in date_list:
            date = date['date_publish'].strftime('%Y年%m月文章归档')
            if date not in distinct_date_list:
                distinct_date_list.append(date)
        return distinct_date_list


class Article(models.Model):
    menu_category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, verbose_name='所属菜单栏类别')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, verbose_name='分类')
    title = models.CharField(max_length=50, verbose_name='文章标题')
    content = models.TextField(verbose_name='文章内容')
    description = models.TextField(max_length=300, verbose_name='文章描述')
    author = models.ForeignKey(MyUser, verbose_name='作者', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags, blank=True, verbose_name='标签')
    photo = models.ImageField(upload_to='articles/%Y/%m/%d/', default='articles/default.jpeg', max_length=200, blank=True, null=True, verbose_name='文章图片')
    views = models.PositiveIntegerField(default=0, verbose_name='文章阅读量')
    date_publish = models.DateTimeField(default=timezone.now, verbose_name='发布时间') # auto_now_add=True,
    objects = ArticleManager()

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        db_table = 'article'
        ordering = ['-date_publish']

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

class Likes(models.Model):
    user = models.ForeignKey(MyUser, verbose_name='点赞者', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='文章', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        db_table = 'likes'

    def __str__(self):
        return str(self.user)

class Comments(models.Model):
    content = models.TextField(verbose_name='评论内容')
    date = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, blank=True, null=True, verbose_name='用户')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, blank=True, null=True, verbose_name='文章')
    pid = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='p_comment', verbose_name='父级评论')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        db_table = 'comments'

    def __str__(self):
        return str(self.id)


