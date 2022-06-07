from django import forms
from django.core.exceptions import ValidationError
from django.conf.urls import url
from django.shortcuts import render, HttpResponse, redirect
from django.utils.safestring import mark_safe

from stark.service.v1 import StarkHandler, StarkModelForm, get_choice_text, StarkForm, Option
from web import models
from stark.utils.md5 import gen_md5
from web.views.base import PermissionHandler


class UserInfoAddForm(StarkModelForm):
    confrim_password = forms.CharField(label='确认密码', )

    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'confrim_password', 'nickname', 'gender', 'phone', 'email', 'depart', 'roles']

    def clean_confrim_password(self):
        password = self.cleaned_data.get('password')
        confrim_password = self.cleaned_data.get('confrim_password')

        if password != confrim_password:
            raise ValidationError('两次密码输入的不一致！')
        return confrim_password

    def clean(self):
        password = self.cleaned_data.get('password')
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


class UserInfoChangeForm(StarkModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name', 'nickname', 'gender', 'phone', 'email', 'depart', 'roles']


class RePasswordForm(StarkForm):
    password = forms.CharField(label='重置密码', widget=forms.PasswordInput)

    confrim_password = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_confrim_password(self):
        password = self.cleaned_data.get('password')

        confrim_password = self.cleaned_data.get('confrim_password')

        if password != confrim_password:
            raise forms.ValidationError('两次密码输入不一致')
        return confrim_password

    def clean(self):
        password = self.cleaned_data.get('password')

        self.cleaned_data['password'] = gen_md5(password)

        return self.cleaned_data


class UserInfoHandler(PermissionHandler, StarkHandler):

    def display_re_password(self, obj=None, is_header=None):
        if is_header:
            return '重置密码'
        return mark_safe('<a href="%s">重置密码</a>' % self.reverse_re_password_url(self.get_re_password_url_name, obj.pk))

    def reverse_re_password_url(self, name, *args, **kwargs):
        return self.reverse_common_url(name, *args, **kwargs)

    list_display = ['name', get_choice_text('性别', 'gender'), 'phone', 'email', 'depart', display_re_password]

    def get_model_form_class(self, add_or_change, request, pk, *args, **kwargs):
        if add_or_change == 'add':
            return UserInfoAddForm
        else:
            return UserInfoChangeForm

    def re_password(self, request, pk):
        user_info_obj = models.UserInfo.objects.filter(pk=pk).first()
        if not user_info_obj:
            return HttpResponse('404')
        if request.method == 'GET':
            form = RePasswordForm()
            return render(request, 'stark/change.html', {'form': form})
        form = RePasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user_info_obj.password = password
            user_info_obj.save()
            return redirect(self.reverse_list_url())

        return render(request, 'stark/change.html', {'form': form})

    @property
    def get_re_password_url_name(self):
        return self.get_url_name('re_password')

    def extra_urls(self):
        patterns = [
            url(r'^re_password/(?P<pk>\d+)/$', self.wrapper(self.re_password), name=self.get_re_password_url_name),
        ]
        return patterns

    search_list = ['nickname__contains', 'name__contains']

    search_group = [
        Option(field='gender'),
        Option(field='depart', is_multi=True),
    ]
