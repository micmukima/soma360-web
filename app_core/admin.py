from django.contrib import admin

from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from app_utils import generate_code


from .models import *

class UserAdminCustom(UserAdmin):
    fieldsets = (

        (_('Personal Information'), {'fields': ('firstname', 'lastname', 'email',
            'contact_phone', 'gender', 'address', 'school', 'profile_picture', 'is_active', 'is_staff')}),
            
       (_('Login Details'), {'fields': ('username', 'password')}),       
                                         
    )
    add_fieldsets = (       
        (_('Personal Information'), {'fields': ('firstname', 'lastname', 'email',
            'contact_phone', 'gender', 'address', 'profile_picture', 'is_active', 'is_staff')}),
                                         
        (_('Login Details'), {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )    
    
    list_display = ('profile_picture_inline', 'email', 'username', 'firstname',
                    'lastname', 'date_registered', 'is_staff', 'school', 'member_groups')
    list_filter = ('is_staff', 'is_active',
                   'groups')
    search_fields = ('username', 'firstname', 'lastname', 'email', 'contact_phone')
    
    def get_form(self, request, obj=None, **kwargs):
        #print request.user.is_superuser
        if request.user.is_superuser:
            self.fieldsets[1][1]["fields"] = ('username', 'is_superuser', 'password', 'groups')
            self.add_fieldsets[1][1]["fields"] = ('username', 'is_superuser', 'password1', 'password2', 'groups')
        form = super(UserAdminCustom,self).get_form(request, obj, **kwargs)
        return form
    
    def get_queryset(self, request):
        qs = super(UserAdminCustom, self).get_queryset(request)
        return qs.filter(school = request.user.school) if request.user.school else qs
        
    def response_add(self, request, obj):    
        administrator_school_id = request.session.get('administrator_school_id', None)   
        password = generate_code(prefix = None, size = 5)
        obj.set_password(password.lower())
        obj.save()
        login_url = settings.LOGIN_LINK
        
        if  administrator_school_id:
        
            group = Group.objects.get(name='School Administrator')
            obj.groups.add(group)
            
            send_mail('New School Administrator Account Created', 'Login Link : %s Login Email : %s Password : %s' %(login_url, obj.email, password.lower()), settings.DEFAULT_FROM_EMAIL, [obj.email, 'micmukima@gmail.com'], fail_silently=False)
            request.session['administrator_school_id'] = None            
            return HttpResponseRedirect("/admin/school/school/")
        else:
            send_mail('New Soma360 Account Created', 'Login Link : %s Login Email : %s Password : %s' %(login_url, obj.email, password.lower()), settings.DEFAULT_FROM_EMAIL, [obj.email, 'micmukima@gmail.com'], fail_silently=False)
            return HttpResponseRedirect("/admin/core/user/")
    
    def save_model(self, request, obj, form, change):
        administrator_school_id = request.session.get('administrator_school_id', None)
        if administrator_school_id:
            obj.school_id = administrator_school_id
        obj.is_staff = True
        obj.save()   
    
    def profile_picture_inline(self, obj):
        if obj.profile_picture:
            return render_to_string('thumbnail.html', {
                'photo': obj.profile_picture
            })
    profile_picture_inline.short_description = "Profile Picture"
    profile_picture_inline.allow_tags = False
    
    def member_groups(self, obj):
        your_string = ' | '.join([str(i.name) for i in obj.groups.all()]) 
        #return u"<a href='%d/'>%s</a>" % (obj.id, your_string)
        return your_string
    member_groups.short_description = "Member Groups"
    member_groups.allow_tags = True
    
class MessagingQueueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['title', 'short_message', 'notification_type', 'student', 'school', 'sms_content', 'mobile_alert_content']
        })
    ]  
    
    list_display = ('title', 'short_message', 'notification_type', 'student', 'school', 'sms_content', 'mobile_alert_content')
    
    def get_queryset(self, request):
        qs = super(MessagingQueueAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)

admin.site.register(User, UserAdminCustom)
admin.site.register(MessagingQueue, MessagingQueueAdmin)
