from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from apps.common.views import *
from apps.book.views import *
from apps.forum.views import *
from apps.calculator.views import *

urlpatterns = [
    # Common
    path('', index),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('profile/<str:username>', Profile.as_view()),
    path('wiki/list', wiki_list),
    path('law/list', law_list),
    path('law', LawView.as_view()),
    path('law/<int:book_id>/init', law_edit_init),
    path('law/<int:page_id>', law_manage, name="law_manage"),
    path('user', user_manage),
    path('user/<int:user_id>', user_update),
    path('forbidden', forbidden),

    # Book
    path('wiki/', wiki_view),
    path('wiki/<int:book_id>', wiki_manage),
    path('wiki/page', wiki_add),
    path('wiki/page/<int:page_id>', wiki_preview),
    path('wiki-editor/<int:book_id>', wiki_page_add),
    path('wiki-editor/page/<int:page_id>', wiki_editor, name="wiki_editor"),
    path('book/<int:book_id>', view_book),
    path('book/bookmark/<int:page_id>', add_or_remove_bookmark),
    path('book/like/<int:book_id>', like_book),
    path('page/<int:page_id>', view_page),
    path('bookmark/', view_bookmark),
    path('bookmark/<int:page_id>', delete_bookmark),
    path('bookmark/label/<int:label_id>', manage_label),

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
