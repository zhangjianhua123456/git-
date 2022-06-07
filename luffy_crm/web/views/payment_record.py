from django.conf.urls import url
from django.shortcuts import HttpResponse
from django import forms

from web import models
from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm
from web.views.base import PermissionHandler


class PaymentRecordForm(StarkModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'note']


class StudentPaymentRecordForm(StarkModelForm):
    qq = forms.CharField(label='QQ', max_length=32)
    mobile = forms.CharField(label='手机号', max_length=32)
    emergency_tel = forms.CharField(label='紧急联系方式', max_length=32)

    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'qq', 'mobile', 'emergency_tel', 'note']


class PaymentRecordHandler(PermissionHandler, StarkHandler):
    list_display = ['customer', get_choice_text('缴费类型', 'pay_type'), 'paid_fee', 'class_list', 'consultant',
                    get_choice_text('状态', 'confirm_status')]

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_list_display(self, request, *args, **kwargs):
        return self.list_display

    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        consult_id = request.session['user_info']['user_id']
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=consult_id)

    def get_model_form_class(self, add_or_change, request, pk, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        student_obj = models.Student.objects.filter(customer_id=customer_id).exists()
        if student_obj:
            return PaymentRecordForm
        return StudentPaymentRecordForm

    def save(self, request, form, is_update, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        consult_id = request.session['user_info']['user_id']
        obj_exist = models.Customer.objects.filter(pk=customer_id, consultant_id=consult_id).exists()

        if not obj_exist:
            return HttpResponse('访问的界面不存在')
        form.instance.customer_id = customer_id
        form.instance.consultant_id = consult_id

        form.save()

        class_list = form.cleaned_data['class_list']
        fetch_student_obj = models.Student.objects.filter(customer_id=customer_id).first()
        if not fetch_student_obj:
            qq = form.cleaned_data['qq']
            mobile = form.cleaned_data['mobile']
            emergency_tel = form.cleaned_data['emergency_tel']
            student_obj = models.Student.objects.create(customer_id=customer_id, qq=qq, mobile=mobile,
                                                        emergency_contract=emergency_tel)
            student_obj.class_list.add(class_list.id)
        else:
            fetch_student_obj.class_list.add(class_list.id)
