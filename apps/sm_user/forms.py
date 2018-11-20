import hashlib
# from encodings.utf_8 import encode

from django import forms

from django.core import validators

from sm_user.models import UserInfo


# 注册验证
class RegForm(forms.Form):
    mobile = forms.CharField(
        max_length=12,
        error_messages={
            "required": "电话必须填写",
            "max_length": "请输入正确的手机号",
        },
        strip=True,
        validators=[
            validators.RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误")
        ],
    )
    password1 = forms.CharField(
        max_length=16,
        min_length=6,
        required=True,
        error_messages={
            "min_length": "密码至少6位数"
        })

    password2 = forms.CharField(required=True, )

    # 验证码
    html_verify = forms.CharField(error_messages={"required": "请填写验证码"})

    # 使用一个方法验证  验证码
    def clean_html_verify(self):
        # html11 = self.data.get("html_verify")
        # htm222 = self.data.get("session_verify")

        html_verify = self.cleaned_data.get("html_verify")
        # session_verify = self.cleaned_data.get("session_verify")

        # html_verify = self.data.get("html_verify")
        session_verify = self.data.get("session_verify")
        if html_verify != str(session_verify):
            raise forms.ValidationError("验证码输入错误")
        return html_verify
    agree = forms.BooleanField()
    # 验证电话是否已经被注册
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        rs = UserInfo.objects.filter(phone=mobile).exists()
        if rs:
            raise forms.ValidationError("该电话号码已经被注册,请重新填写")
        else:
            return mobile

    # 最后验证,输入的密码是否一致
    def clean(self):
        # cleaned_data = super().clean()
        cleaned_data = self.cleaned_data
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        if pw1:
            if pw1 != pw2:
                raise forms.ValidationError({
                    "password2": "两次密码不一致"
                })
            else:
                if all((pw1, pw2)):
                    h = hashlib.sha1(pw1.encode("utf-8"))
                    pwd = h.hexdigest()
                    cleaned_data['password1'] = pwd
                    return cleaned_data


# 登录验证
class LoginForm(forms.Form):
    mobile = forms.CharField(
        max_length=12,
        strip=True,
        required=True,
        error_messages={
            "required": "用户名/手机号必须填写"
        },
        validators=[
            validators.RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误")
        ],
    )
    password = forms.CharField(required=True,
                               error_messages={
                                   "required": "密码不能为空"
                               }, )


# 用户信息修改
class User_Info_Alter(forms.ModelForm):
    pass
