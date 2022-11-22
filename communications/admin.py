from django.contrib import admin

from .models import *
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from app_utils.select_lists import *
from django.urls import path, re_path
from django.utils.html import format_html


class MessageAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': ['student', 'recipient_class', 'title', 'priority', \
                'sms_message', 'mobile_alert_message', 'email_message']
        })
    ]  
    
    list_display = ('student', 'recipient_class', 'title', 'priority', \
        'sms_message', 'mobile_alert_message', 'email_message', \
        'edit_message_link', 'send_message_link')
        
    list_filter = ('sent', 'date_created', 'priority')
    search_fields = ('student', 'title', 'sms_message', 'mobile_alert_message', 'email_message')
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'recipient_class': 
            kwargs['queryset'] = get_school_classes(request)
        if db_field.name == 'student': 
            kwargs['queryset'] = get_school_students(request)
        return super(MessageAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
    
    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)
    
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.created_by = request.user
        obj.save()
        
    def send_message_link(self, obj):
        if obj.sent == 1:
            return format_html("<span class='label label-info'>Queued for Sending</span>")
        elif obj.sent == 2:
            return format_html("<span class='label label-success'>Sent</span>")
        else:
            return format_html("<a href='%d/send_message'>%s</a>" % (obj.id, "Send Message &raquo;"))
    send_message_link.short_description = ""
    send_message_link.allow_tags = True
    
    def edit_message_link(self, obj):
        if not obj.sent == 0:
            return format_html("<span class='label label-info'>Edit Locked</span>")
        return format_html("<a href='%d/'>%s</a>" % (obj.id, "Edit"))
    #edit_message_link.short_description = ""
    #edit_message_link.allow_tags = True
    
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        
        urls = [
            #path(r'^(.+)/send_message/$', self.send_message, name='%s_%s_send_message' % info),
        ]

        super_urls = super(MessageAdmin, self).get_urls()

        return urls + super_urls
        
    def send_message(self, request, message_id, form_url='', extra_context=None):
        try:
            message_details = get_object_or_404(Message, pk=message_id)
        except Message.DoesNotExist:
            message_details = None
         
        if message_details and message_details.sent == 0:
            message_details.sent = 1 #  0 to 1 queues a message sending then 2 marks as sent
            message_details.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
class EventAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': ['student', 'event_class', 'event_title', 'event_date', 'event_time', 'venue', 'event_details']
        })
    ]
    
    list_display = ('student', 'event_class', 'event_title', 'event_date', 'event_time', 'venue', 'event_details', 'created_by', 'date_created', 'send_notification_link')
        
    list_filter = ('notified', 'date_created', 'event_time')
    search_fields = ('event_title', 'event_details')
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'event_class': 
            kwargs['queryset'] = get_school_classes(request)
        if db_field.name == 'student': 
            kwargs['queryset'] = get_school_students(request)
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
    
    def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)
    
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.created_by = request.user
        obj.save()
        
    def send_notification_link(self, obj):
        if obj.notified == 1:
            return format_html("<span class='label label-info'>Queued for Notification</span>")
        elif obj.notified == 2:
            return format_html("<span class='label label-success'>Sent</span>")
        else:
            return format_html("<a href='%d/send_notification'>%s</a>" % (obj.id, "Send Notification &raquo;"))
    
    
    def edit_message_link(self, obj):
        if not obj.notified == 0:
            return format_html("<span class='label label-info'>Edit Locked</span>")
        return format_html("<a href='%d/'>%s</a>" % (obj.id, "Edit"))
    
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            re_path(r'^(.+)/send_notification/$', self.send_notification, name='%s_%s_send_notification' % info),
        ]

        super_urls = super(EventAdmin, self).get_urls()

        return my_urls + super_urls
        
    def send_notification(self, request, event_id, form_url='', extra_context=None):
        try:
            event_details = get_object_or_404(Event, pk=event_id)
        except Event.DoesNotExist:
            event_details = None
         
        if event_details and event_details.notified == 0:
            event_details.notified = 1 #  0 to 1 queues a message sending then 2 marks as sent
            event_details.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
class SchoolVideosAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': ['title', 'video_link', 'video_id', 'description', 'is_published', 'is_sent']
        })
    ]  
    
    list_display = ('title', 'video_link', 'video_id', 'description', 'is_published', 'is_sent', 'publish_video_link')
        
    list_filter = ('is_published', 'is_sent')
    search_fields = ('title', 'video_link', 'video_id', 'description')
    
    def publish_video_link(self, obj):
        if obj.is_published == 1:
            return format_html("<span class='label label-info'>Published</span>")
        return format_html("<a href='%d/publish_video'>%s</a>" % (obj.id, "Publish Video"))
    publish_video_link.short_description = ""
    publish_video_link.allow_tags = True
    
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        
        urls = [
            #path(r'^(.+)/publish_video/$', self.publish_video, name='%s_%s_publish_video' % info),
        ]
        super_urls = super(SchoolVideosAdmin, self).get_urls()

        return urls + super_urls
        
    def publish_video(self, request, video_id, form_url='', extra_context=None):
        try:
            video_details = get_object_or_404(SchoolVideos, pk=video_id)
        except SchoolVideos.DoesNotExist:
            video_details = None
         
        if video_details and video_details.is_published == 0:
            video_details.is_published = 1 #  0 to 1 queues a message sending then 2 marks as sent
            video_details.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    
    
    def get_queryset(self, request):
        qs = super(SchoolVideosAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)
    
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.created_by = request.user
        obj.save()
        
class SchoolFeedAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': ['title', 'photo', 'banner_address', 'video_link', 'video_id', 'description', 'is_published', 'is_sent']
        })
    ]  
    
    list_display = ('title', 'photo_inline', 'banner_address', 'video_link', 'video_id', 'description', 'is_published', 'is_sent', 'publish_feed_link')
        
    list_filter = ('is_published', 'is_sent')
    search_fields = ('title', 'video_link', 'video_id', 'description')
    
    def photo_inline(self, obj):
        if obj.photo:
            return render_to_string('thumbnail.html', {
                'photo': obj.photo
            })
    photo_inline.short_description = "Feed Photo"
    photo_inline.allow_tags = False
    
    def publish_feed_link(self, obj):
        if obj.is_published == 1:
            return format_html("<span class='label label-info'>Published</span>")
        return format_html("<a href='%d/publish_feed'>%s</a>" % (obj.id, "Publish"))
    publish_feed_link.short_description = ""
    publish_feed_link.allow_tags = True
    
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        
        urls = [
            #path(r'^(.+)/publish_feed/$', self.publish_feed, name='%s_%s_publish_feed' % info),
        ]
        super_urls = super(SchoolFeedAdmin, self).get_urls()

        return urls + super_urls
        
    def publish_feed(self, request, feed_id, form_url='', extra_context=None):
        try:
            feed_details = get_object_or_404(SchoolFeed, pk=feed_id)
        except SchoolFeed.DoesNotExist:
            feed_details = None
         
        if feed_details and feed_details.is_published == 0:
            feed_details.is_published = 1 #  0 to 1 queues a message sending then 2 marks as sent
            feed_details.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

admin.site.register(Message, MessageAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(SchoolVideos, SchoolVideosAdmin)
admin.site.register(SchoolFeed, SchoolFeedAdmin)
