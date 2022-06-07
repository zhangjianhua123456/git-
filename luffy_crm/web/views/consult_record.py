from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse

from stark.service.v1 import StarkHandler, StarkForm, StarkModelForm
from web import models
from web.views.base import PermissionHandler


class ConsultRecordHandler(StarkModelForm):
    class Meta:
        model = models.CounsultRecord
        fields = ['note']


class ConsultRecordHandler(PermissionHandler, StarkHandler):
    model_form_class = ConsultRecordHandler

    list_display = ['note', 'consultant', 'date']

    def display_edit(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列（表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "编辑"
        return mark_safe('<a href="%s">编辑</a>' % self.reverse_change_url(pk=obj.pk, customer_id=kwargs['customer_id']))

    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "删除"
        return mark_safe('<a href="%s">删除</a>' % self.reverse_delete_url(pk=obj.pk, customer_id=kwargs['customer_id']))

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs["customer_id"]
        consult_id = request.session['user_info']['user_id']
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=consult_id)

    def save(self, request, form, is_update, *args, **kwargs):
        customer_id = kwargs['customer_id']
        consult_id = request.session['user_info']['user_id']
        obj = models.Customer.objects.filter(id=customer_id, consultant_id=consult_id)
        if not obj:
            return HttpResponse("非法操作")
        if not is_update:
            form.instance.customer_id = customer_id
            form.instance.consultant_id = consult_id
        form.save()

    def get_change_obj(self, request, pk, *args, **kwargs):
        consult_id = request.session['user_info']['user_id']
        customer_id = kwargs.get('customer_id')
        return self.model_class.objects.filter(pk=pk, customer_id=customer_id, consultant_id=consult_id).first()

    def get_del_obj(self, request, pk, *args, **kwargs):
        consult_id = request.session['user_info']['user_id']
        customer_id = kwargs.get('customer_id')
        obj = self.model_class.objects.filter(pk=pk, customer_id=customer_id, consultant_id=consult_id)
        if obj:
            obj.delete()
        else:
            return HttpResponse("非法操作")

    change_list_template = 'web/consult_record.html'
