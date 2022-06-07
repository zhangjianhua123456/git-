from stark.service.v1 import site
from web import models

from web.views.course import CourseHandler
from web.views.userinfo import UserInfoHandler
from web.views.depart import DepartmentHandler
from web.views.school import SchoolHandler

from web.views.class_list import ClassListHandler
from web.views.public_customer import PubCustomerHandler
from web.views.private_custmoer import PriCustomerHandler
from web.views.consult_record import ConsultRecordHandler
from web.views.payment_record import PaymentRecordHandler
from web.views.check_payment_record import CheckPaymentRecord
from web.views.student import StudentHandler
from web.views.score_record import ScoreRecordHandler
from web.views.course_record import CourseRecordHandler

site.register(models.School, SchoolHandler)

site.register(models.Department, DepartmentHandler)

site.register(models.UserInfo, UserInfoHandler)

site.register(models.Course, CourseHandler)

site.register(models.ClassList, ClassListHandler)

site.register(models.Customer, PubCustomerHandler, prev='pub')

site.register(models.Customer, PriCustomerHandler, prev='pri')

site.register(models.CounsultRecord, ConsultRecordHandler)

site.register(models.PaymentRecord, PaymentRecordHandler)

site.register(models.PaymentRecord, CheckPaymentRecord, prev='check')

site.register(models.Student, StudentHandler)

site.register(models.ScoreRecord, ScoreRecordHandler)

site.register(models.CourseRecord, CourseRecordHandler)
