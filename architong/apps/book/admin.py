from django.db import models
from django.contrib import admin
from martor.widgets import AdminMartorWidget
from apps.book.models import Pages

class PageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

admin.site.register(Pages, PageAdmin)