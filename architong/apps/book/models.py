from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator


class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_title = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    author_id = models.CharField(max_length=150)
    cover_path = models.CharField(max_length=255, blank=True, null=True)
    rls_yn = models.CharField(max_length=10)
    like_cnt = models.IntegerField(blank=True, null=True)
    wrt_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enfc_dt = models.DateTimeField(blank=True, null=True)
    codes_yn = models.CharField(max_length=10, blank=True, null=True)
    mdfcn_dt = models.DateTimeField(auto_now=True)
    hit_count = models.IntegerField(blank=True, null=True, default=0)
    CODE_CHOICES = (
        ('0', '법령'), ('1', '행정규칙'), ('2', '자치법규')
    )
    WIKI_CHOICES = (
        ('0', '전체'), ('1', '설계'), ('2', '재료'), ('3', '시공'),
        ('4', '설비'), ('5', '환경'), ('6', '도시'), ('7', '기타')
    )
    code_gubun = models.CharField(max_length=2, choices=CODE_CHOICES)
    wiki_gubun = models.CharField(max_length=10, blank=True, null=True, choices=WIKI_CHOICES)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserLikeBook')

    class Meta:
        managed = False
        db_table = 'books'


class UserLikeBook(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)
    reg_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_like_book'


class Pages(models.Model):
    page_id = models.AutoField(primary_key=True)
    book_id = models.IntegerField()
    page_title = models.CharField(max_length=255)
    parent_id = models.IntegerField(blank=True, null=True, default=0)
    depth = models.IntegerField(blank=True, null=True, default=0)
    description = models.TextField(blank=True, null=True)
    wrt_dt = models.DateTimeField(auto_now_add=True)
    mdfcn_dt = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'pages'


class BookmarkLabel(models.Model):
    label_id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'bookmark_label'


class Bookmark(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    page_id = models.IntegerField()
    book_id = models.IntegerField()
    username = models.CharField(max_length=150)
    reg_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    label = models.ForeignKey(BookmarkLabel, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bookmark'
