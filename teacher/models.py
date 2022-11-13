from django.db import models
from django.utils import timezone

from app_core.models import User, UserManager

class Teacher(User):
    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s" %(self.firstname, self.lastname)

    def __unicode__(self):
        return "%s %s" %(self.firstname, self.lastname)
