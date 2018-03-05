from django.contrib import admin
from BU.models import *

# Register your models here.


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'qq', 'mobile', 'age', 'avatar', )

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'tags_all', 'views', 'date_publish', 'category', 'menu_category', 'photo', )
    filter_horizontal = ('tags',)
    list_per_page = 10
    list_filter = ('date_publish',)
    raw_id_fields = ('author',)
    search_fields = ('title', 'author__username',)

    class Media:
        js = (
            '/static/js/kindeditor-4.1.10/kindeditor-min.js',
            '/static/js/kindeditor-4.1.10/lang/zh_CN.js',
            '/static/js/kindeditor-4.1.10/config.js',
        )

    def tags_all(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])



class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'pid', 'content', 'date', 'id' )
    list_per_page = 10
    search_fields = ('user', 'article', )
    raw_id_fields = ('pid',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'index')
    list_per_page = 10
    search_fields = ('name',)

class TagsAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_fields = ('name',)

class LikesAdmin(admin.ModelAdmin):
    list_display = ('user', 'article')
    list_per_page = 10

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuCategory)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Likes, LikesAdmin)

