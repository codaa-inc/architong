from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from apps.common.views import *
from apps.book.views import *
from apps.forum.views import *


urlpatterns = [
    # Common
    path('admin/', admin.site.urls),
    path('', index),
    path('accounts/', include('allauth.urls')),
    path('profile/', profile),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('get_law/', LawView.as_view()),

    # Book
    path('edit/', editor),
    path('book/<int:book_id>', view_book),
    path('book/bookmark/<int:page_id>', add_or_remove_bookmark),
    path('page/<int:page_id>', view_page),
    path('bookmark/', view_bookmark),
    path('bookmark/<int:page_id>', delete_bookmark),
    path('comment/count/', comment_count),

    # Forum
    path('comment/<str:id>', CommentView.as_view()),
    path('comment/update/<str:id>', comment_update),
    path('comment/like/<str:comment_id>', like_comment),
    path('forum/', forum),
    path('forum/<int:comment_id>', forum_detail),
]
