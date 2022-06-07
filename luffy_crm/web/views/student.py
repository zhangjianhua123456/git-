from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.urls import reverse

from stark.service.v1 import StarkHandler, get_m2m_text, get_choice_text, StarkModelForm, Option
from web import models
from web.views.base import PermissionHandler


class StudentForm(StarkModelForm):
    class Meta:
        model = models.Student
        fields = ['qq', 'mobile', 'emergency_contract', 'memo']


class StudentHandler(PermissionHandler, StarkHandler):
    model_form_class = StudentForm

    def display_score(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '积分'
        reverse_url = reverse('stark:web_scorerecord_list', kwargs={"customer_id": obj.pk})
        return mark_safe('<a target="_blank" href="%s">%s</a>' % (reverse_url, obj.score))

    list_display = ['customer', 'mobile', 'emergency_contract', get_m2m_text('已报班级', 'class_list'),
                    get_choice_text('学员状态', 'student_status'), display_score]

    def get_add_btn(self, request, *args, **kwargs):
        return None

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit)
        return value

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            # url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            # url(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    search_list = ['qq__contains', 'mobile__contains', 'customer__name']

    search_group = [
        Option(field='class_list', text_func=lambda x: '%s-%s' % (x.school, x))
    ]
