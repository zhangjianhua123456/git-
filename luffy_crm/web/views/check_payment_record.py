from django.conf.urls import url

from stark.service.v1 import StarkHandler, get_choice_text, get_time_text, Option
from web import models
from web.views.base import PermissionHandler


class CheckPaymentRecord(PermissionHandler, StarkHandler):
    order_list = ['confirm_status', '-id', ]

    list_display = [StarkHandler.display_checkbox,
                    'customer', get_choice_text('费用类型', 'pay_type'), 'paid_fee', 'class_list',
                    get_time_text('申请日期', 'apply_date'),
                    get_choice_text('当前状态', 'confirm_status'), 'consultant',
                    ]

    def get_list_display(self, request, *args, **kwargs):
        return self.list_display

    def get_add_btn(self, request, *args, **kwargs):
        return None

    def action_multi_comfire(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            obj = self.model_class.objects.filter(pk=pk, confirm_status=1).first()
            if not obj:
                continue
            obj.confirm_status = 2
            obj.save()

            obj.customer.status = 1
            obj.customer.save()

            obj.customer.student.student_status = 2
            obj.customer.student.save()

    action_multi_comfire.text = '批量确认'

    def action_multi_cancel(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list, confirm_status=1).update(confirm_status=3)

    action_multi_cancel.text = '批量驳回'

    action_list = [action_multi_cancel, action_multi_comfire]

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            # url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            # url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            # url(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    search_group = [
        Option(field='pay_type'),
        Option(field='confirm_status'),
    ]
