from stark.service.v1 import StarkHandler
from web.views.base import PermissionHandler


class DepartmentHandler(PermissionHandler, StarkHandler):
    list_display = ['title']