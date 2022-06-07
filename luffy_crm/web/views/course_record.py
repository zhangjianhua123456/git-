from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse, render
from django.forms.models import modelformset_factory

from stark.service.v1 import StarkHandler, StarkModelForm, get_time_text
from web import models
from web.views.base import PermissionHandler


class CourseRecordForm(StarkModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ['day_num', 'teacher']


class StudyRecordForm(StarkModelForm):
    class Meta:
        model = models.StudyRecord
        fields = ['record']


class CourseRecordHandler(PermissionHandler, StarkHandler):

    def display_attendance(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "考勤记录"
        name = self.get_url_name('attendance')
        return mark_safe('<a href="%s">考勤记录</a>' % self.reverse_common_url(name, course_record_id=obj.pk))

    list_display = [StarkHandler.display_checkbox, 'day_num', 'teacher', get_time_text('记录日期', 'date'),
                    display_attendance]

    model_form_class = CourseRecordForm

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<class_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<class_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                name=self.get_delete_url_name),
            url(r'^attendance/(?P<course_record_id>\d+)/$', self.wrapper(self.attendance_views),
                name=self.get_url_name('attendance')),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def attendance_views(self, request, course_record_id, *args, **kwargs):
        study_record_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        form_obj = modelformset_factory(models.StudyRecord, form=StudyRecordForm, extra=0)

        if request.method == 'POST':
            formset = form_obj(data=request.POST, queryset=study_record_list)
            if formset.is_valid():
                formset.save()
            return render(request, 'web/attendance.html', {"formset": formset})

        formset = form_obj(queryset=study_record_list)

        return render(request, 'web/attendance.html', {"formset": formset})

    def display_edit(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列（表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "编辑"
        return mark_safe('<a href="%s">编辑</a>' % self.reverse_change_url(pk=obj.pk, class_id=kwargs['class_id']))

    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "删除"
        return mark_safe('<a href="%s">删除</a>' % self.reverse_delete_url(pk=obj.pk, class_id=kwargs['class_id']))

    def get_queryset(self, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        return self.model_class.objects.filter(class_object_id=class_id)

    def save(self, request, form, is_update, *args, **kwargs):
        class_id = kwargs.get('class_id')
        if not is_update:
            form.instance.class_object_id = class_id
        form.save()

    def action_multi_init(self, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        course_pk_list = request.POST.get('pk')
        # 判断当前url的班级信息是否存在
        class_obj = models.ClassList.objects.filter(pk=class_id).first()

        if not class_obj:
            return HttpResponse('班级不存在')

        # 查出所有的学生信息
        student_obj_list = class_obj.student_set.all()

        # 遍历课程记录
        for course_pk in course_pk_list:

            # 判断当前班级是否存在这个课程记录
            course_obj_exists = models.CourseRecord.objects.filter(class_object_id=class_id, pk=course_pk).exists()
            if not course_obj_exists:
                return HttpResponse('非法操作')

            # 判断上课记录的考勤是否已存在
            study_record_exists = models.StudyRecord.objects.filter(course_record_id=course_pk).exists()
            if study_record_exists:
                continue

            # 批量初始化
            student_stu_list = [models.StudyRecord(course_record_id=course_pk, student_id=stu.pk) for stu in
                                student_obj_list]

            models.StudyRecord.objects.bulk_create(student_stu_list)

    action_multi_init.text = '批量初始化考勤'

    action_list = [action_multi_init]
