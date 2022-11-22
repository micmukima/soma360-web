from django.db import models
from django.utils.translation import ugettext_lazy as _
from app_utils import generate_code
from sorl.thumbnail import ImageField
from django.utils import timezone

from app_core.models import User
from django.db.models import Q


class Parent(User):
    profession = models.CharField('Profession', max_length=255, blank=True)
    code = models.CharField("Parent's Code", max_length=255, blank=True, null=True)
        
    @property
    def total_children(self):
        from student.models import Student
        return Student.objects.filter(Q(parent_1=self) | Q(parent_2=self)).count()
        
    @property
    def children(self):
        from student.models import Student
        return Student.objects.filter(Q(parent_1=self) | Q(parent_2=self))
        
    def save(self, * args, ** kwargs):    
        if not self.code:
            self.code = generate_code(prefix = None, size = 5)
        super(Parent, self).save( * args, ** kwargs)
    
    class Meta:
        verbose_name = 'Parent'
        verbose_name_plural = 'Parents'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s" %(self.first_name, self.last_name)

    def __unicode__(self):
        return "%s %s" %(self.first_name, self.last_name)
