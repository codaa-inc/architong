from django.db import models
from martor.models import MartorField
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
    CODE_CHOICES = (
        ('0', '법령'),
        ('1', '행정규칙'),
        ('2', '자치법규'),
    )
    code_gubun = models.CharField(max_length=2, choices=CODE_CHOICES)
    hit_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'


class Pages(models.Model):
    page_id = models.AutoField(primary_key=True)
    book_id = models.IntegerField()
    page_title = models.CharField(max_length=255)
    parent_id = models.IntegerField(blank=True, null=True, default=0)
    depth = models.IntegerField(blank=True, null=True, default=0)
    description = MartorField(blank=True, null=True)
    wrt_dt = models.DateTimeField(auto_now_add=True)
    mdfcn_dt = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'pages'


class Bookmark(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    page_id = models.IntegerField()
    book_id = models.IntegerField()
    username = models.CharField(max_length=150)
    reg_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bookmark'
