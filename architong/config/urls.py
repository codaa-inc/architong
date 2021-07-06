from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from apps.common.views import *
from apps.book.views import *
from apps.forum.views import *
from apps.calculator.views import *


urlpatterns = [
    # Common
    path('admin/', admin.site.urls),
    path('', index),
    path('martor/', include('martor.urls')),
    path('accounts/', include('allauth.urls')),
    path('profile/<str:username>', profile),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('law/insert', LawView.as_view()),
    path('law/update/<int:book_id>', law_update),
    path('law/manage', manage_law),
    path('user/manage', manage_user),
    path('user/update/<int:user_id>', user_update),

    # Book
    path('wiki/', wiki_manage),
    path('wiki/add', wiki_add),
    path('wiki/<int:book_id>', wiki_update),
    path('wiki/edit/<int:book_id>', wiki_add_page),
    path('wiki/edit/page/<int:page_id>', wiki_editor),
    path('wiki/delete/<int:book_id>', wiki_delete),
    path('wiki/delete/page/<int:page_id>', wiki_delete_page),
    path('wiki/page/<int:page_id>', wiki_page_viewer),
    path('book/law', law_list),
    path('book/wiki', wiki_list),
    path('book/<int:book_id>', view_book),
    path('book/bookmark/<int:page_id>', add_or_remove_bookmark),
    path('book/like/<int:book_id>', like_book),
    path('page/<int:page_id>', view_page),
    path('bookmark/', view_bookmark),
    path('bookmark/<int:page_id>', delete_bookmark),
    path('testmd', testmd),

    # Forum
    path('comment/<str:id>', CommentView.as_view()),
    path('comment/update/<str:id>', comment_update),
    path('comment/count/', comment_count),
    path('comment/like/<str:comment_id>', like_comment),
    path('forum/', forum),
    path('forum/<str:comment_id>', forum_detail),

    # Calculator
    path('calc/uvalue', uvalue),
    path('m.calc/uvalue', uvalue_m),
    path('calc/uvalue/data', uvalue_data),

]
