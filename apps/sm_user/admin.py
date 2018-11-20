from django.contrib import admin

# Register your models here.
from sm_user.models import UserInfo


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    pass










