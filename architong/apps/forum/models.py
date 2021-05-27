from django.db import models
from datetime import datetime, timedelta, timezone


class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    page_id = models.IntegerField()
    parent_id = models.IntegerField()
    depth = models.IntegerField()
    username = models.CharField(max_length=150)
    content = models.TextField(blank=True, null=True)
    rls_yn = models.CharField(max_length=10, blank=True, null=True)
    reg_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    @property
    def created_string(self):
        time = datetime.now() - self.reg_dt
        if time < timedelta(minutes=1):
            return '방금 전'
        elif time < timedelta(hours=1):
            return str(int(time.seconds / 60)) + '분 전'
        elif time < timedelta(days=1):
            return str(int(time.seconds / 3600)) + '시간 전'
        elif time < timedelta(days=7):
            time = datetime.now(tz=timezone.utc).date() - self.reg_dt.date()
            return str(time.days) + '일 전'
        else:
            return False

    class Meta:
        managed = False
        db_table = 'comments'
