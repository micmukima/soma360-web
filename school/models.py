from django.db import models
from django.utils.translation import ugettext_lazy as _
from app_utils import generate_code
from sorl.thumbnail import ImageField
from django.utils import timezone
from django.conf import settings

from tinymce import models as tinymce_models
from student.models import Student
from parent.models import Parent

SCHOOL_TYPES = (
    ('primary', "Primary School"), 
    ('Secondary', "Secondary School"), 
    ('early_learning', "Early Learning"), 
    #('college', "College"),
    #('university', "University"),
)
    
class School(models.Model):    
    code = models.CharField('School Code', max_length=255, blank=True)
    name = models.CharField('School Name', max_length=255, blank=False)
    type = models.CharField('School Type', max_length=200, choices=SCHOOL_TYPES, blank=False)
    address = models.TextField('School Address', max_length=255, blank=True)
    contact_person = models.CharField(max_length=255, blank=False)
    contact_phone = models.CharField(max_length=255, blank=False)
    contact_email = models.EmailField('E-mail Address', max_length=255, blank=True)
    date_registered = models.DateTimeField(default=timezone.now) 
    school_logo = ImageField(upload_to='images/school_logos/%Y/%m', default=None, blank=True)
        
    @property
    def total_students(self):
        return Student.objects.filter(school = self).count()
        
    @property
    def total_parents(self):
        return Parent.objects.filter(school = self).count()
        
    @property
    def academic_year(self):
        return AcademicYear.objects.filter(school_id = self.id).first()
        
    @property
    def current_term(self):
        return SchoolTerm.objects.filter(school_id = self.id).first()
        
        
    def save(self, * args, ** kwargs):    
        if not self.code:
            prefix = reduce(lambda x,y: x+y[0].upper(),self.name.split(),'')
            self.code = generate_code(prefix = prefix[:2], size = 8)
        super(School, self).save( * args, ** kwargs)
    
    class Meta:
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s" %(self.name)

    def __unicode__(self):
        return "%s" %(self.name)
 
 
class Class(models.Model):
    name = models.CharField('Class Name', max_length=255, blank=False)
    numeric_name = models.IntegerField('Numeric Name', blank=False)   
    description = models.TextField('Class Description', max_length=255, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=False)
    teacher = models.ForeignKey('teacher.Teacher', on_delete=models.PROTECT, blank=True, null=True, verbose_name= _('Class Teacher'))
        
    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Class'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s" %(self.name)

    def __unicode__(self):
        return "%s" %(self.name)
               
class Section(models.Model): # class streams
    name = models.CharField('Section Name', max_length=255, blank=False)
    description = models.TextField('Section Description', max_length=255, blank=False)
    date_created = models.DateTimeField(default=timezone.now)
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=False)
        
    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s" %(self.name)

    def __unicode__(self):
        return "%s" %(self.name)
        
class Subject(models.Model):
    short_name = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)
    date_created = models.DateTimeField(default=timezone.now)
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=False)
        
    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subject'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s" %(self.name)

    def __unicode__(self):
        return "%s" %(self.name)
        
class AcademicYear(models.Model):
    numeric_year = models.IntegerField(blank=False)
    description = models.TextField(max_length=255, blank=True)
    currently_active = models.BooleanField(default=False)
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=False, null=False)    
     
    class Meta:
        verbose_name = 'School Year'
        verbose_name_plural = 'School Years'
        unique_together = ("numeric_year", "school")
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return str(self.numeric_year)
        
    def __unicode__(self):
        return str(self.numeric_year)
        
class ClassSubject(models.Model):
    school_class = models.ForeignKey('Class', on_delete=models.PROTECT, blank=False)
    section = models.ForeignKey('Section', on_delete=models.PROTECT, blank=True, null=True)
    teacher = models.ForeignKey('teacher.Teacher', on_delete=models.PROTECT, blank=True, null=True)
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, blank=False)
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.CASCADE, blank=False, null=True)
            
    class Meta:
        verbose_name = 'Class Subjects'
        verbose_name_plural = 'Class Subjects'
        default_permissions = ('add', 'change', 'delete', 'view')
        unique_together = ("school_class", "section", "teacher", "subject", "academic_year")
        
    def __str__(self):
        return "%s" %(self.school_class.name)

    def __unicode__(self):
        return "%s" %(self.school_class.name)

class SchoolTerm(models.Model):
    name = models.CharField(max_length=255, blank=False)
    start_date = models.DateField()
    end_date = models.DateField()
    currently_active = models.BooleanField(default=False,
        help_text='Currently active school term.')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        verbose_name = 'School Term'
        verbose_name_plural = 'School Terms'
        default_permissions = ('add', 'change', 'delete', 'view')
        
    def __str__(self):
        return "%s %s" %(self.name, self.academic_year)

    def __unicode__(self):
        return "%s %s" %(self.name, self.academic_year)
