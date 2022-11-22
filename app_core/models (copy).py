from django.db import models
from django.conf import settings
import re
import uuid
from django.utils.dateformat import format

from django.core import validators
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Q
from django import forms

USER = settings.AUTH_USER_MODEL

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, lastname, firstname, gender, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')

        user = self.model(username=username, gender=gender,
                          lastname=lastname, firstname=firstname,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_registered=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, lastname, firstname, gender,
                    password=None, **extra_fields):
        return self._create_user(username, lastname, firstname, gender,
                                 password, False, False, **extra_fields)

    def create_superuser(self, username, lastname, firstname, gender,
                         password, **extra_fields):
        return self._create_user(username, lastname, firstname, gender,
                                 password, True, True, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.SlugField(_('username'), max_length=50, unique=True,
        help_text=_('Required. 50 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    firstname = models.CharField(_('firstname'), max_length=255, blank=True)
    lastname = models.CharField(_('lastname'), max_length=100, blank=True)
    gender = models.CharField(_('gender'), max_length=6, blank=True,
                              choices=(('male', 'Male'), ('female', 'Female')))
                              
    address = models.TextField('Address', max_length=255, blank=True)
        
    email = models.EmailField(_('email address'), blank=True, null=True,
                              unique=True)
    contact_phone = models.CharField(_('phone number'), max_length=100, blank=True, null=True,
                               unique=False)
    profile_picture = models.ImageField(upload_to='profile', blank=True)
    is_staff = models.BooleanField(_('staff status'), default=True,
        help_text=_('Only staff can directly login to the admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user can login to the system. Deactivate users instead of deleting accounts.'))

        
    date_registered = models.DateTimeField(_('date registered'), default=timezone.now)

    android_device_id = models.CharField(max_length=200,blank=True)
    
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, blank=True, null=True, related_name = 'member_school')
    
    sms_notification = models.BooleanField(default=False)
    mobile_notification = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=False)
        
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstname', 'lastname', 'gender']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s" %(self.lastname, self.firstname)

    def __unicode__(self):
        return "%s %s" %(self.lastname, self.firstname)

    def get_full_name(self):
        """
        Returns the firstname plus the lastname, with a space in between.
        """
        full_name = '%s %s' % (self.firstname, self.lastname)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.firstname
        
    @property
    def date_created(self):
        return format(self.date_registered, 'U')
        
    @property
    def total_pupils(self):
        from student.models import Student
        return Student.objects.filter(Q(parent_1=self) | Q(parent_2=self)).count()
        
    @property
    def parent_schools(self):
        import json
        schools_dict = []
        from school.models import School
        schools = School.objects.filter(pk = self.school.id)
        for sch in schools:
            schools_dict.append({
                'id' : sch.id,
                'name' : sch.name,
                'contact_phone' : sch.contact_phone
            });
        return json.dumps(schools_dict)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.username:
            max_length = self.__class__._meta.get_field('username').max_length
            self.username = orig = slugify(self.lastname)[:max_length]
            for x in itertools.count(1):
                if not self.__class__.objects.filter(username=self.username).exists():
                    break
                self.username = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
        else:
            self.username = slugify(self.username)
        if not self.email:
            self.email = None
        if not self.contact_phone:
            self.contact_phone = None
        super(User, self).save(force_insert=force_insert,
            force_update=force_update, using=using, update_fields=update_fields)
            
class MessagingQueue(models.Model):
    title =  models.CharField(max_length=255, blank=True, null=True)
    short_message =  models.TextField(blank=True, null=True)
    notification_type =  models.CharField(max_length=50, blank=True, null=True)
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, blank=True, null=True)
    term = models.ForeignKey('school.SchoolTerm', on_delete=models.CASCADE, blank=True, null=True)
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, blank=True, null=True)
    academic_year = models.ForeignKey('school.AcademicYear', on_delete=models.CASCADE, blank=True, null=True)    
    sms_content = models.TextField()
    email_content = models.TextField()
    mobile_alert_content = models.TextField()    
    is_processed = models.BooleanField(default=False)  
    date_created = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Messaging Queue'
        verbose_name_plural = 'Messaging Queue'
        default_permissions = ('add', 'change', 'delete', 'view')

    @property
    def date_created_timestamp(self):
        return format(self.date_created, 'U')
        
    def __str__(self):
        return "%s %s" %(self.title, self.short_message)

    def __unicode__(self):
        return "%s %s" %(self.title, self.short_message)
