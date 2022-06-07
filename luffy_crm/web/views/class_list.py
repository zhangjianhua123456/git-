from django.utils.safestring import mark_safe
from django.urls import reverse

from stark.service.v1 import StarkHandler, StarkModelForm, get_time_text, get_m2m_text
from stark.forms.widgets import Datetimepicker
from web.models import ClassList
from web.views.base import PermissionHandler


class ClassListForm(StarkModelForm):
    class Meta:
        model = ClassList
        fields = '__all__'
        widgets = {
            "start_date": Datetimepicker,
            "graduate": Datetimepicker,
        }


class ClassListHandler(PermissionHandler, StarkHandler):

    model_form_class = ClassListForm

    def display_course_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '上课记录'
        reverse_url = reverse('stark:web_courserecord_list', kwargs={'class_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">上课记录</a>' % reverse_url)

    def display_class_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '班级名称'
        return '%s(%s)期' % (obj.course.name, obj.semester)

    list_display = ['school', 'price', display_class_name, get_time_text('开班日期', 'start_date'), 'class_teacher',
                    get_m2m_text('任课老师', 'tech_teacher'), display_course_record]

