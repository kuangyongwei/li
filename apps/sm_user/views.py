import random
import re
import uuid

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

# Create your views here.
from django.urls import reverse
from django.views import View

# 个人中心
from sm_user.forms import RegForm, LoginForm
from sm_user.models import UserInfo
from sm_user.public import check_user_pwd, check_user, session_decorator, send_sms


# 登录
class LoginView(View):
    def get(self, request):
        return render(request, "sm_user/login.html")

    def post(self, request):
        # 点击登录提交数据,验证
        login_data = request.POST
        form = LoginForm(login_data)

        # 在form中验证合法
        if form.is_valid():
            # 获取from的清洗数据
            clean_data = form.cleaned_data
            user1 = clean_data.get("mobile")
            pwd = clean_data.get("password")

            # 先检查用户名是否在数据库中存在,如果不存在,则抛出用户名不存在的错误
            user = check_user(user1)

            # 如果存在
            if user:
                # 得到用户名/电话,进行验证得到检查结果
                check_result = check_user_pwd(user1, pwd)

                # 电话以及密码正确的情况下,设置session,进入用户资料页面
                if check_result:
                    request.session.clear()
                    request.session["ID"] = check_result.id
                    request.session["username"] = check_result.phone
                    request.session.set_expiry(0)
                    if request.GET.get("next"):
                        return redirect(request.GET.get("next"))
                    return redirect(reverse("sm_user:member"))
                else:

                    # 密码错误的情况下需要抛出错误
                    form.errors['password'] = ["密码错误,请重新输入"]
                    context = {
                        "errors": form.errors
                    }

                return render(request, "sm_user/login.html", context=context)

            # 用户名如果不存在
            else:
                form.errors['mobile'] = ["用户名不存在"]
                context = {
                    "errors": form.errors
                }
            return render(request, "sm_user/login.html", context=context)

        # 验证不合法的情况下
        else:
            errors = {
                "errors": form.errors,
            }
            # print(11)
            return render(request, "sm_user/login.html", context=errors)
            # return HttpResponse("验证失败")


# 注册
class RegView(View):
    def get(self, request):
        return render(request, "sm_user/reg.html")

    def post(self, request):
        # 现将session中的验证码取出来

        session_verify = request.session.get("session_verify")
        # 将session中的验证码装到request.POST里面
        data = request.POST.dict()
        data["session_verify"] = str(session_verify)

        data11=request.POST.get("html_verify")
        # 将数据得到后交到form表单验证,验证码一起验证
        form = RegForm(data)
        # mobile = request.POST.get("mobile")
        # password1 = request.POST.get("password1")
        # password2 = request.POST.get("password2")
        # data111111=form.cleaned_data
        if form.is_valid():
            clean_data = form.cleaned_data
            mobile = clean_data.get("mobile")
            password1 = clean_data.get("password1")
            # password2 = clean_data.get("password2")
            # print(mobile)
            # print(password2)
            # print(password1)
            # 将三个数据添加到数据库
            UserInfo.objects.create(phone=mobile, pwd=password1)

            return render(request, 'sm_user/login.html', )
        else:
            errors = {
                "errors": form.errors,
            }
            # print(11)
            return render(request, "sm_user/reg.html", context=errors)


# 个人资料及其修改
class InfoView(View):
    @session_decorator
    def get(self, request):
        # 通过request中的session得到登录用户的
        user_id = request.session.get("ID")
        # 到数据库查询当前用户信息
        user_info = UserInfo.objects.filter(id=user_id).first()
        try:
            # 数据库保存有时间的情况下
            user_data = user_info.data.strftime('%Y-%m-%d')
            user = {
                "userinf": user_info,
                "user_data": user_data
            }
            return render(request, "sm_user/infor.html", context=user)
        except AttributeError:
            # 数据库保存没有保存时间会报错,因为没有时间,所以没有strftime属性
            user_info = {
                "userinf": user_info,
            }
            return render(request, "sm_user/infor.html", context=user_info)

    def post(self, request):
        id = request.session.get("ID")
        nickname = request.POST.get("nickname")
        sex = request.POST.get("sex")
        data = request.POST.get("data")
        school = request.POST.get("school")
        address = request.POST.get("address")
        hometown = request.POST.get("hometown")
        UserInfo.objects.filter(id=id).update(nickname=nickname, sex=sex, data=data, school=school,
                                              address=address, hometown=hometown)
        # print(data)
        return redirect(reverse("sm_user:info"))


# 个人中心
class MemberView(View):
    @session_decorator
    def get(self, request):
        return render(request, "sm_user/member.html")

    def post(self, request):
        return HttpResponse("个人资料")


# 短信发送 视图函数
def sendMsg(request):
    """
        发送验证码
        :param request:
        :return:
    """
    # 接收到手机号码
    tel = request.GET.get('phone', '0')
    # # 验证号码格式是否正确
    r = re.compile('^1[3-9]\d{9}$')
    res = re.search(r, tel)
    print(res)
    if res is None:
        return JsonResponse({"ok": 0, "msg": "手好号码格式错误!"})

    # 随机生成验证码
    code = random.randint(100000, 999999)
    # # 保存到session中 ,等你验证的时候使用
    request.session['session_verify'] = code
    # # 设置过期时间 redis
    request.session.set_expiry(60*60)
    print(code)
    print("==================================")

    # # # 生成一个唯一的字符串
    # __business_id = uuid.uuid1()
    # print(__business_id)
    # 模板中的变量
    # params = "{\"code\":\"%s\"}" % code

    rs = send_sms(__business_id, tel, "匡伟", "SMS_142080039", params)
    # rs = rs.decode("utf-8")
    rs = {"Code": "OK"}
    #
    if rs['Code'] == "OK":
        return JsonResponse({"ok": 1})
    else:
        return HttpResponse({"ok": 0, "msg": "短信发送失败"})
    # return HttpResponse(code)
