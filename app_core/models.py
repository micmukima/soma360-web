from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

class MyUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given username must be set')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    username = models.CharField(_('username'), max_length=50, unique=False,
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

    first_name = models.CharField(_('first_name'), max_length=255, blank=True)
    last_name = models.CharField(_('last_name'), max_length=100, blank=True)
    gender = models.CharField(_('gender'), max_length=6, blank=True,
                              choices=(('male', 'Male'), ('female', 'Female')))
                              
    address = models.TextField('Address', max_length=255, blank=True)

    contact_phone = models.CharField(_('phone number'), max_length=100, blank=True, null=True,
                           unique=False)
    profile_picture = models.ImageField(upload_to='profile', blank=True)
    is_staff = models.BooleanField(_('staff status'), default=True,
        help_text=_('Only staff can directly login to the admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user can login to the system. Deactivate users instead of deleting accounts.'))

        
    date_registered = models.DateTimeField(_('date registered'), default=timezone.now)

    android_device_id = models.CharField(max_length=200,blank=True)

    school = models.ForeignKey("school.School", on_delete=models.CASCADE, blank=True, null=True, related_name = 'member_school')

    sms_notification = models.BooleanField(default=False)
    mobile_notification = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class MessagingQueue(models.Model):
    title =  models.CharField(max_length=255, blank=True, null=True)
    short_message =  models.TextField(blank=True, null=True)
    notification_type =  models.CharField(max_length=50, blank=True, null=True)
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, blank=True, null=True)
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
