from django.contrib import admin
from django import forms
from .models import *
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.shortcuts import render
from django.urls import path, re_path


class ParentForm(forms.ModelForm):

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
        return super(ParentForm, self).save(commit=commit)

    class Meta:
        model = Parent
        fields = '__all__'

class ParentAdmin(admin.ModelAdmin):  

    form = ParentForm
      
    fieldsets = [
        ('Personal Information', {
            'fields': ['first_name', 'last_name', 'email', 'date_of_birth', 'contact_phone', 'gender', 'address', 'profession', 'profile_picture']
        }),
        ('Login Details', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Notifications', {
            'classes': ('wide',),
            'fields': ('sms_notification', 'mobile_notification', 'email_notification'),
        }),  
        
    ]   
    
    list_display = ('parent_photo_inline', 'parent_detail_view_link','first_name' , 'last_name', 'email', 'contact_phone', 'address', 'date_registered', 'edit_parent_link')
    list_filter = ('date_registered',)
    search_fields = ('first_name', 'last_name', 'email', 'contact_phone', 'address', 'profession') 
    
    def get_queryset(self, request):
        qs = super(ParentAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def save_model(self, request, obj, form, change):
        
            
        if form.cleaned_data['password2']:
            obj.set_password(form.cleaned_data['password2'])
            
        obj.school = request.user.school
        obj.save()
        
        """if not change: # set group on first create parent
            group = Group.objects.get(name='Parent')
            obj.groups.add(group)"""
        
    def parent_photo_inline(self, obj):
        if obj.profile_picture:
            return render_to_string('thumbnail.html', {
                'photo': obj.profile_picture
            })
    parent_photo_inline.short_description = "Photo"
    
    def edit_parent_link(self, obj):
        return """
            <div class='dropdown'>
              <a class='btn btn-default dropdown-toggle' data-toggle='dropdown'>Actions
              <span class='caret'></span></a>
              <ul class='dropdown-menu'>
                <li>
                    <a href='%d/'><i class='icon-edit'></i> Edit</a>
                </li>
                <li>
                    <a class='modal-click' data-toggle='modal' data-target='.full-content-slider' data-title='%s %s' href='%d/parent_detail_view'><i class='icon-eye-open'></i> More Details</a>
                </li>
              </ul>
            </div>
        """ %(obj.id, obj.first_name, obj.last_name, obj.id)
    edit_parent_link.short_description = 'Actions'
    edit_parent_link.allow_tags = True
    
    def parent_detail_view_link(self, obj):
        return u"<a href='%d/parent_detail_view' class='modal-click' data-toggle='modal' data-target='.full-content-slider' data-title='%s %s'>%s</a>" % (obj.id, obj.first_name, obj.last_name, obj.first_name)
    parent_detail_view_link.short_description = "First Name"
    parent_detail_view_link.allow_tags = True
    
    def get_urls(self):
        #from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)


        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            re_path(r'^(.+)/parent_detail_view/$', self.parent_detail_view, name='%s_%s_parent_detail_view' % info),
        ]

        super_urls = super(ParentAdmin, self).get_urls()

        return my_urls + super_urls

    def parent_detail_view(self, request, parent_id, form_url='', extra_context=None):
        from django import forms
        from django.shortcuts import get_object_or_404
        opts = Parent._meta
                
        try:
            parent_details = get_object_or_404(Parent, pk=parent_id)
        except Parent.DoesNotExist:
            parent_details = None
        
        context = {
            'title': 'Parent Details : %s' % parent_details,
            'has_change_permission': self.has_change_permission(request, parent_details),
            'opts': opts,
            'app_label': opts.app_label,
            'parent_details': parent_details,
        }
        context.update(extra_context or {})

        return render(request, 'parent_detail_view.html', context)

admin.site.register(Parent, ParentAdmin)
