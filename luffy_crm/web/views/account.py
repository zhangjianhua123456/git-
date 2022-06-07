from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse

from stark.utils.md5 import gen_md5
from web import models
from rbac.service.init_permission import init_permission


def login(request):
    if request.method == 'GET':
        return render(request, 'web/login.html')
    user = request.POST.get("username")
    pwd = gen_md5(request.POST.get("pwd", ""))

    user = models.UserInfo.objects.filter(name=user, password=pwd).first()
    if not user:
        return render(request, 'web/login.html', {"errmsg": "用户名或密码错误"})
    request.session["user_info"] = {"user_id": user.pk, "nickname": user.nickname}
    init_permission(user, request)
    return redirect(reverse('index'))


def logout(request):
    request.session.delete()

    return redirect(reverse('login'))


def index(request):
    return render(request, 'web/index.html')
