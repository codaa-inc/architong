from django.db import models

class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    page_id = models.IntegerField()
    parent_id = models.IntegerField()
    depth = models.IntegerField()
    username = models.CharField(max_length=150)
    content = models.TextField(blank=True, null=True)
    rls_yn = models.CharField(max_length=10, blank=True, null=True)
    reg_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'
