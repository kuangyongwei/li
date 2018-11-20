import hashlib
from django.shortcuts import redirect
from sm_user.models import UserInfo

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from django.conf import settings
from django.shortcuts import redirect, reverse

from dysms_python.aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from sm_user.models import  UserInfo


# 检查用户名以及密码是否存在
def check_user_pwd(user, pwd):
    h = hashlib.sha1(str(pwd).encode('utf-8'))
    password = h.hexdigest()
    return UserInfo.objects.filter(phone=user, pwd=password).first()


# 检查用户名是否存在
def check_user(user):
    return UserInfo.objects.filter(phone=user).first()


# 写一个验证session的装饰器
def session_decorator(fun):
    def verify(*args, **kwargs):
        # 如果没有session,返回登录界面
        if args[1].session.get("ID") is None:
            return redirect("sm_user:login")
        else:
            return fun(*args, **kwargs)

    return verify


# 阿里自带发送短信的方法
def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    # 注意：不要更改
    REGION = "cn-hangzhou"
    PRODUCT_NAME = "Dysmsapi"
    DOMAIN = "dysmsapi.aliyuncs.com"

    acs_client = AcsClient(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET, REGION)
    region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)

    # 数据提交方式
    # smsRequest.set_method(MT.POST)

    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理

    return smsResponse
