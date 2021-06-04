from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    act_point = models.IntegerField(default=0, blank=True, null=False)


class SocialaccountSocialaccount(models.Model):
    id = models.BigAutoField(primary_key=True)
    provider = models.CharField(max_length=30)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.TextField()
    user = models.ForeignKey(UserInfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)
