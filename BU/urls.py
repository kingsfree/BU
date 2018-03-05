from django.conf.urls import url
from BU import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^article_list', views.article_list, name='article_list'),
    url(r'^article', views.article, name='article'),
    url(r'^project', views.project, name='project'),
    url(r'^life', views.life, name='life'),
    url(r'^topics', views.topics, name='topics'),
    url(r'^archive', views.archive, name='archive'),
    url(r'^category', views.category, name='category'),
    url(r'^tag', views.tagPage, name='tagpage'),
    url(r'^logout$', views.do_logout, name='logout'),
    url(r'^comment$', views.comment_post, name='comment_post'),
    url(r'^ajax_login', views.ajax_login, name='ajax_login'),
    url(r'^ajax_signup', views.ajax_signup, name='ajax_signup'),
    url(r'^email', views.ajax_email, name='ajax_email'),
    url(r'^reset_password', views.reset_password, name='reset_password'),
    url(r'^like', views.likes_set, name='like'),
    url(r'^avatar', views.avatar_upload, name='avatar_upload'),
    url(r'^publicate_article', views.article_publicate, name='article_publicate'),
    url(r'^userinfo', views.userinfo, name='userinfo'),
    url(r'^deletearticle', views.articleDelete, name='article_delete'),
    url(r'^editarticle', views.articleEdit, name='article_edit'),
    url(r'^search', views.search, name='search'),
    url(r'^resultpage', views.resultpage, name='resultpage'),
]