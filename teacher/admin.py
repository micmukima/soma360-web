from django.contrib import admin
from django.conf import settings
from .models import *
from django.template.loader import render_to_string
from django.shortcuts import render
from django import forms
from django.contrib.auth.models import Group
from app_utils import generate_code
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import path, re_path
from django.utils.html import format_html

class TeacherForm(forms.ModelForm):

    username = models.CharField(max_length=100)
    password1 = forms.CharField(widget=forms.PasswordInput, required = False)
    password2 = forms.CharField(widget=forms.PasswordInput, required = False)
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 or password2: # only validate if password is set
            if not password2:
                raise forms.ValidationError("You must confirm your password")
            if password1 != password2:
                raise forms.ValidationError("Your passwords do not match")
        return password2

    def save(self, commit=True):
        username = self.cleaned_data.get('username', None)
        password1 = self.cleaned_data.get('password1', None)
        return super(TeacherForm, self).save(commit=commit)

    class Meta:
        model = Teacher
        fields = '__all__'

class TeacherAdmin(admin.ModelAdmin):   
    
    form = TeacherForm
    
    fieldsets = (       
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'contact_phone', 'gender', 'address', 'profile_picture')}),
                                         
        ('Login Details', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('teacher_logo_inline', 'teacher_detail_view_link', 'email', 'contact_phone', 'gender', 'address', 'date_registered', 'edit_teacher_link')
    list_filter = ('date_registered', )
    search_fields = ('first_name', 'last_name', 'address', 'email', 'contact_phone') 
    
    def get_queryset(self, request):
        qs = super(TeacherAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def response_add(self, request, obj):
        password = generate_code(prefix = None, size = 5)
        obj.set_password(password.lower())
        obj.save()
        login_url = settings.LOGIN_LINK
        """send_mail('New School Instructor Account Created', 'Login Link : %s Login Email : %s Password : %s' %(login_url, obj.email, password.lower()), settings.DEFAULT_FROM_EMAIL, [obj.email, 'micmukima@gmail.com'], fail_silently=False)"""
        
        return HttpResponseRedirect("/admin/teacher/teacher/")

        
    def save_model(self, request, obj, form, change):
        
            
        if form.cleaned_data['password2']:
            obj.set_password(form.cleaned_data['password2'])
            
        obj.school = request.user.school
        obj.save()
        
        """if not change: # set group on first create teacher
            group = Group.objects.get(name='Teacher')
            obj.groups.add(group)"""
    
    def teacher_logo_inline(self, obj):
        if obj.profile_picture:
            return render_to_string('thumbnail.html', {
                'photo': obj.profile_picture
            })
    teacher_logo_inline.short_description = "Photo"
    teacher_logo_inline.allow_tags = False
    
    def edit_teacher_link(self, obj):
        return format_html("""
            <div class='dropdown'>
              <a class='btn btn-default dropdown-toggle' data-toggle='dropdown'>Actions
              <span class='caret'></span></a>
              <ul class='dropdown-menu'>
                <li>
                    <a href='%d/'><i class='icon-edit'></i> Edit</a>
                </li>
                <li>
                    <a class='modal-click' data-toggle='modal' data-target='.full-content-slider' data-title='%s %s' href='%d/teacher_detail_view'><i class='icon-eye-open'></i> More Details</a>
                </li>
              </ul>
            </div>
        """ %(obj.id, obj.first_name, obj.last_name, obj.id))
    
    def teacher_detail_view_link(self, obj):
        return format_html("<a href='%d/school_detail_view' data-toggle='modal' class='modal-click' data-target='.full-content-slider', data-title='%s %s'>%s %s</a>" % (obj.id, obj.first_name, obj.last_name, obj.first_name, obj.last_name))
        
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            re_path(r'^(.+)/teacher_detail_view/$', self.teacher_detail_view, name='%s_%s_teacher_detail_view' % info),
        ]

        super_urls = super(TeacherAdmin, self).get_urls()

        return my_urls + super_urls

    def teacher_detail_view(self, request, teacher_id, form_url='', extra_context=None):
        from django import forms
        from django.shortcuts import get_object_or_404
        opts = Teacher._meta
                
        try:
            teacher_details = get_object_or_404(Teacher, pk=teacher_id)
        except Teacher.DoesNotExist:
            teacher_details = None
        
        context = {
            'title': 'Teacher Details : %s' % teacher_details,
            'has_change_permission': self.has_change_permission(request, teacher_details),
            'opts': opts,
            'app_label': opts.app_label,
            'teacher_details': teacher_details,
        }
        context.update(extra_context or {})

        return render(request, 'teacher_detail_view.html', context)
        
admin.site.register(Teacher, TeacherAdmin)
