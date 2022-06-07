from django.conf.urls import url

from stark.service.v1 import StarkHandler, StarkModelForm
from web import models
from web.views.base import PermissionHandler


class ScoreRecordHandler(StarkModelForm):
    class Meta:
        model = models.ScoreRecord
        fields = ['content', 'score']


class ScoreRecordHandler(PermissionHandler, StarkHandler):
    list_display = ['content', 'score', 'user']

    def get_list_display(self, request, *args, **kwargs):
        return self.list_display

    model_form_class = ScoreRecordHandler

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def save(self, request, form, is_update, *args, **kwargs):
        student_id = kwargs.get('customer_id')
        consult_id = request.session['user_info']['user_id']
        form.instance.student_id = student_id
        form.instance.user_id = consult_id
        form.save()

        score = form.instance.score

        if score > 0:
            form.instance.student.score += abs(score)
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()

    def get_queryset(self, request, *args, **kwargs):
        student_id = kwargs.get('customer_id')
        return self.model_class.objects.filter(student_id=student_id)
