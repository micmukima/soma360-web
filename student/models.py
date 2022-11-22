from django.db import models
from django.utils.translation import ugettext_lazy as _
from app_utils import generate_code
from sorl.thumbnail import ImageField
from django.utils import timezone

from app_core.models import User
from parent.models import Parent


class Student(models.Model):
    first_name = models.CharField('First Name', max_length=255, blank=False)
    middle_name = models.CharField('Middle Name', max_length=255, blank=False)
    last_name = models.CharField('Last Name', max_length=255, blank=False)
    parent_1 = models.ForeignKey(Parent, on_delete=models.PROTECT, related_name="parent_1", blank=False)
    parent_2 = models.ForeignKey(Parent, on_delete=models.PROTECT, related_name="parent_2", blank=True, null=True)
    address = models.TextField('Address', max_length=255, blank=False)
    registration_number = models.CharField('Registration Number', max_length=255, blank=True)
    date_registered = models.DateTimeField(default=timezone.now)
    current_class = models.ForeignKey('school.Class', on_delete=models.PROTECT, related_name="parent_1", blank=False)
    current_section = models.ForeignKey('school.Section', on_delete=models.PROTECT, related_name="parent_1", blank=True, null=True)
    current_academic_year = models.ForeignKey('school.AcademicYear', on_delete=models.CASCADE, blank=False, null=False) 
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, blank=True, null=True)   
       
    photo = ImageField(
        upload_to='images/student_photos/%Y/%m',
        default=None, blank=True)
        
       
    @property 
    def student_names(self):
        return "%s %s %s" %(self.first_name, self.middle_name, self.last_name)
        
    def save(self, * args, ** kwargs):    
        if not self.registration_number:
            self.registration_number = generate_code(prefix = None, size = 5)
        super(Student, self).save( * args, ** kwargs)
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s %s" %(self.first_name, self.middle_name, self.last_name)

    def __unicode__(self):
        return "%s %s %s" %(self.first_name, self.middle_name, self.last_name)
        
class StudentBulkAdmit(Student): # mass import from excel
    class Meta:
        verbose_name = 'Student Bulk Admit'
        verbose_name_plural = 'Student Bulk Admit'
        default_permissions = ('add', 'change', 'delete', 'view')
        proxy = True
        
        
class StudentPromotion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, blank=False)
    from_class = models.ForeignKey('school.Class', on_delete=models.PROTECT, related_name="from_class", blank=False)
    to_class = models.ForeignKey('school.Class', on_delete=models.PROTECT, related_name="to_class", blank=False)
    from_section = models.ForeignKey('school.Section', on_delete=models.PROTECT, related_name="from_section", blank=False)
    to_section = models.ForeignKey('school.Section', on_delete=models.PROTECT, related_name="to_section", blank=False)
    from_academic_year = models.ForeignKey('school.AcademicYear', on_delete=models.CASCADE, blank=False, null=False, related_name='from_academic_year')
    to_academic_year = models.ForeignKey('school.AcademicYear', on_delete=models.CASCADE, blank=False, null=False, related_name='to_academic_year')
    promoted_by = models.ForeignKey('app_core.User', on_delete=models.PROTECT, blank=True, null=True)
    date_promoted = models.DateTimeField(default=timezone.now)    
    
    class Meta:
        verbose_name = 'Student Promotion'
        verbose_name_plural = 'Student Promotions'        
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s %s" %(self.student, self.from_class, self.to_class)

    def __unicode__(self):
        return "%s %s %s" %(self.student, self.from_class, self.to_class)
