from django.db import models

from db.base_model import BaseModel


# Create your models here.

# 用户信息表
class UserInfo(BaseModel):
    sex_choices = (
        (1, "男"),
        (2, "女"),
        (3, "不详"),
    )
    nickname = models.CharField(
        max_length=15,
        verbose_name="昵称",
        null=True, blank=True
    )
    # upload_to为图片的上传位置
    phone = models.CharField(max_length=12, unique=True, verbose_name="电话号码")
    pwd = models.CharField(max_length=64, verbose_name="密码")
    sex = models.SmallIntegerField(choices=sex_choices, null=True, blank=True)
    data = models.DateField(null=True, blank=True)
    school = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    hometown = models.CharField(max_length=20, null=True, blank=True)
    picture = models.ImageField(upload_to='user_head/%Y%m/%d', default='user_head/infortx.png', verbose_name='头像LOGO')

    def __str__(self):
        return self.phone

    class Meta():
        verbose_name = "用户管理"
        verbose_name_plural = verbose_name
