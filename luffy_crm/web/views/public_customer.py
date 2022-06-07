from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, render
from django.db import transaction

from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm, get_m2m_text
from web import models
from web.views.base import PermissionHandler


class PubCustomerForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant']


class PubCustomerHandler(PermissionHandler, StarkHandler):

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    def display_customerrecord(self, obj=None, is_header=None):
        if is_header:
            return '跟进记录'
        return mark_safe(
            '<a href="%s">跟进记录</a>' % (self.reverse_common_url(self.get_url_name('record_customer'), pk=obj.pk)))

    list_display = [StarkHandler.display_checkbox, 'name', 'qq', get_choice_text('状态', 'status'),
                    get_m2m_text('咨询课程', 'course'),
                    get_choice_text('就业状态', 'work_status'), display_customerrecord, ]
    model_form_class = PubCustomerForm

    def record_customer(self, request, pk):
        data_info = models.CounsultRecord.objects.filter(customer_id=pk)
        if data_info:
            return render(request, 'web/custmoer_record.html', {'date_info': data_info})
        return HttpResponse("没有跟进记录")

    def extra_urls(self):
        patterns = [
            url(r'^record_customer/(?P<pk>\d+)/$', self.wrapper(self.record_customer),
                name=self.get_url_name('record_customer')),
        ]
        return patterns

    def action_multi_aply(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')

        consultant = request.session['user_info']['user_id']
        """
        models.Customer.objects.filter(pk__in=pk_list, status=2, consultant__isnull=True).update(consultant_id=consultant)
        """
        pre_private_count = models.Customer.objects.filter(consultant_id=consultant, status=2).count()
        # 私户中未报名的客户数量限制
        if pre_private_count + len(pk_list) > models.Customer.MAX_PRIVATE_COUNT:
            return HttpResponse('你的私户人数已有%s人还处于未报名状态，只能再添加%s人，操作失败' % (
                pre_private_count, models.Customer.MAX_PRIVATE_COUNT - pre_private_count))
        # 数据库数据枷锁
        flage = False
        with transaction.atomic():
            # 上锁
            update_queryset = models.Customer.objects.filter(pk__in=pk_list, status=2,
                                                             consultant__isnull=True).select_for_update()
            # 判读数据个数是否相同
            if update_queryset.count() == len(pk_list):
                models.Customer.objects.filter(pk__in=pk_list, status=2, consultant__isnull=True).update(
                    consultant_id=consultant)
                flage = True

        if not flage:
            return HttpResponse('手速慢了, 选中的可以已被别人选走！')

    action_multi_aply.text = '添加到私户'

    action_list = [action_multi_aply]

