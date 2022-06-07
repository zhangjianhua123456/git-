from django.utils.safestring import mark_safe
from django.urls import reverse

from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm
from web import models
from web.views.base import PermissionHandler


class PriCustomerForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant']


class PriCustomerHandler(PermissionHandler, StarkHandler):
    model_form_class = PriCustomerForm

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(
            consultant_id=self.request.session["user_info"]["user_id"])

    def display_consult_record(self, obj=None, is_header=None):
        if is_header:
            return "跟进记录"
        reverse_url = reverse("stark:web_counsultrecord_list", kwargs={'customer_id': obj.pk})
        return mark_safe('<a href="%s" target="-blank">跟进记录</a>' % reverse_url)

    def display_payment(self, obj=None, is_header=None):
        if is_header:
            return "缴费"
        reverse_url = reverse("stark:web_paymentrecord_list", kwargs={'customer_id': obj.pk})
        return mark_safe('<a href="%s" target="-blank">缴费记录</a>' % reverse_url)

    list_display = [StarkHandler.display_checkbox, 'name', 'qq', get_choice_text('状态', 'status'),
                    get_m2m_text('咨询课程', 'course'),
                    get_choice_text('就业状态', 'work_status'), display_consult_record, display_payment]

    def save(self, request, form, is_update, *args, **kwargs):
        if not is_update:
            form.instance.consultant_id = request.session["user_info"]["user_id"]
        form.save()

    def action_multi_remove(self, request, *args, **kwargs):
        remove_list_pk = request.POST.getlist("pk")

        self.model_class.objects.filter(pk__in=remove_list_pk,
                                        consultant_id=request.session['user_info']['user_id']).update(consultant=None)

    action_multi_remove.text = "移除到公户"

    action_list = [
        action_multi_remove,
    ]
