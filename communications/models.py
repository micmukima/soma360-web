from django.db import models

from django.utils import timezone
from django.utils.dateformat import format

MESSAGE_PRIORITY = (
    ("normal", "Normal"),
    ("urgent", "Urgent"),
    ("low", "Low")
)

class Message(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, blank=True, null=True)
    recipient_class = models.ForeignKey('school.Class', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    priority = models.CharField(max_length=120, blank=True, null=True,
        choices=MESSAGE_PRIORITY, default="normal"
    )
    sms_message = models.TextField()
    mobile_alert_message = models.TextField()
    email_message = models.TextField()
    sent = models.IntegerField(default=0)  
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, blank=True, null=True) 
    created_by = models.ForeignKey('app_core.User', on_delete=models.CASCADE, blank=True, null=True) 
    date_created = models.DateTimeField(default=timezone.now)
    
    @property
    def date_created_timestamp(self):
        return format(self.date_created, 'U')
        
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        default_permissions = ('add', 'change', 'delete', 'view')
        
    def __unicode__(self):
        return self.title
        
class Event(models.Model):
    event_title = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.TimeField()
    venue = models.CharField(max_length=255)
    event_details = models.TextField()
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, blank=True, null=True)
    event_class = models.ForeignKey('school.Class', on_delete=models.CASCADE, blank=True, null=True)
    notified = models.IntegerField(default=0)  
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, blank=True, null=True) 
    created_by = models.ForeignKey('app_core.User', on_delete=models.CASCADE, blank=True, null=True) 
    date_created = models.DateTimeField(default=timezone.now)
    
    @property
    def event_date_cleaned(self):
        return self.event_date.strftime('%d %B %Y')
        
    @property
    def event_time_cleaned(self):
        return self.event_date.strftime('%I:%M %p')
        
    @property
    def date_created_timestamp(self):
        return format(self.date_created, 'U')
        
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        default_permissions = ('add', 'change', 'delete', 'view')
        
    def __unicode__(self):
        return self.event_title
        
class SMSOutQueue(models.Model):
    message_ref =  models.ForeignKey('app_core.MessagingQueue', on_delete=models.CASCADE, blank=True, null=True)
    sms_content = models.TextField()
    recipient_mobile =  models.CharField(max_length=50, blank=True, null=True)
    date_sent = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=255, blank=True, null=True)
    is_sent = models.BooleanField(default=False)
        
    class Meta:
        verbose_name = 'SMS Out Queue'
        verbose_name_plural = 'SMS Out Queue'
        unique_together = ("message_ref", "recipient_mobile")
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s" %(self.recipient_mobile, self.sms_content)

    def __unicode__(self):
        return "%s %s" %(self.recipient_mobile, self.sms_content)
        
class AndroidAlertOutQueue(models.Model):
    message_ref =  models.ForeignKey('app_core.MessagingQueue', on_delete=models.CASCADE, blank=True, null=True)
    #sms_content = models.TextField()
    #recipient_mobile =  models.CharField(max_length=50, blank=True, null=True)
    alert_content = models.TextField()
    device_id =  models.CharField(max_length=255)                 
    title =  models.CharField(max_length=255)
    message =  models.CharField(max_length=400)
    notification_type  =  models.CharField(max_length=255)
    student_id  =   models.IntegerField()
    student_name = models.CharField(max_length=255)
    
    date_sent = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=255, blank=True, null=True)
    is_sent = models.BooleanField(default=False)
        
    class Meta:
        verbose_name = 'Android Alert Out Queue'
        verbose_name_plural = 'Android Alert Out Queue'
        unique_together = ("message_ref", "device_id")
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s" %(self.recipient_mobile, self.sms_content)

    def __unicode__(self):
        return "%s %s" %(self.recipient_mobile, self.sms_content)



class EmailOutQueue(models.Model):
    message_ref =  models.ForeignKey('app_core.MessagingQueue', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)            
    email_content = models.TextField()
    recipient_email =  models.EmailField()
    date_sent = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=255, blank=True, null=True)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Email Out Queue'
        verbose_name_plural = 'Email Out Queue'
        unique_together = ("message_ref", "recipient_email")
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return "%s %s" %(self.recipient_email, self.title)

    def __unicode__(self):
        return "%s %s" %(self.recipient_email, self.title)
        
class SchoolVideos(models.Model):
    title =  models.CharField(max_length=255, blank=False)
    video_link =  models.CharField(max_length=255, blank=False)
    video_id = models.CharField(max_length=255, blank=False)
    description = models.TextField()
    date_added = models.DateTimeField(default=timezone.now)
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, blank=True, null=True) 
    is_published = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
        
    class Meta:
        verbose_name = 'School Video'
        verbose_name_plural = 'School Videos'
        default_permissions = ('add', 'change', 'delete', 'view')
        
    @property
    def date_added_timestamp(self):
        return format(self.date_added, 'U')

    def __str__(self):
        return self.title
        
        
class SchoolFeed(models.Model):
    title =  models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='feed_photo', blank=True)
    banner_address = models.CharField(max_length=255, blank=True)
    video_link =  models.CharField(max_length=255, blank=True)
    video_id = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
        
    class Meta:
        verbose_name = 'Soma360 Feed'
        verbose_name_plural = 'Soma360 Feed'
        default_permissions = ('add', 'change', 'delete', 'view')
        
    @property
    def date_added_timestamp(self):
        return format(self.date_added, 'U')

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
