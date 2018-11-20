from django.conf.urls import url

from sm_user.views import MemberView, LoginView, RegView, InfoView, sendMsg

urlpatterns = [
    url(r'^member/$', MemberView.as_view(), name="member"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^reg/$', RegView.as_view(), name="reg"),
    url(r'^info/$', InfoView.as_view(), name="info"),
    url(r'^sendMsg/$', sendMsg, name='sendMsg'),  # 发短信

]
