import re
from student.models import Student
from school.models import Subject, ClassSubject, SchoolTerm
from django.conf import settings

def user_is_teacher(current_user):
    user_groups = current_user.groups.values_list('name',flat=True)
    return settings.TEACHER_GROUP_NAME in user_groups
    
def clean_mobile_number(mobile_number):
    if not mobile_number:
        return None
    clean_mobile = re.sub("[^0-9]", "", mobile_number)
    if clean_mobile[:1] == '0':
        clean_mobile = "254" + clean_mobile[1:]
    return clean_mobile
