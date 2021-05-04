from django.db import models
from martor.models import MartorField

class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_title = models.CharField(max_length=255)
    author_id = models.CharField(max_length=150)
    cover_path = models.CharField(max_length=255, blank=True, null=True)
    rls_yn = models.CharField(max_length=10)
    like_cnt = models.IntegerField(blank=True, null=True)
    wrt_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'


class Pages(models.Model):
    page_id = models.AutoField(primary_key=True)
    book_id = models.IntegerField()
    page_title = models.CharField(max_length=255)
    parent_id = models.IntegerField(blank=True, null=True)
    depth = models.IntegerField(blank=True, null=True)
    description = MartorField()
    wrt_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    mdfcn_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pages'
