from django.contrib import admin
import datetime
from .models import *
from teacher.models import Teacher
from django.template.loader import render_to_string
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django import forms
from django.contrib import admin, messages
from app_utils.select_lists import *

from django.urls import path, re_path
from django.utils.html import format_html

from app_utils.list_filters import SectionListFilter, ClassesListFilter, \
    ClassesListFilter, AcademicYearListFilter, SubjectsListFilter
        
class TeachersListFilter(admin.SimpleListFilter):
    title = 'Teacher'
    parameter_name = 'teacher_id'

    def lookups(self, request, model_admin):
        unique_teacher = []
        qs = Teacher.objects.filter(school = request.user.school)
        return set([(related_obj.id, related_obj) for related_obj in qs])
    def queryset(self, request, queryset):
        return queryset


class SchoolAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['name', 'type', 'address', 'contact_person', 'contact_phone', 'contact_email', 'school_logo']
        })
    ]   
    
    list_display = ('school_logo_inline', 'school_detail_view_link', 'name', 'address', 'contact_person', 'contact_phone', 'contact_email', 'date_registered', 'edit_school_link')
    list_filter = ('date_registered',)
    search_fields = ('name', 'address', 'contact_person__surname', 'contact_person__other_names', 'contact_person__email', 'contact_phone') 
    
    def school_logo_inline(self, obj):
        if obj.school_logo:
            return format_html(render_to_string('thumbnailx90.html', {
                'photo': obj.school_logo
            }))
    
    def edit_school_link(self, obj):
        return format_html("""
            <div class='dropdown'>
              <a class='btn btn-default dropdown-toggle' data-toggle='dropdown'>Actions
              <span class='caret'></span></a>
              <ul class='dropdown-menu'>
                <li>
                    <a href='%d/'><i class='icon-edit'></i> Edit</a>
                </li>
                <li>
                    <a class='modal-click' data-toggle='modal' data-target='.full-content-slider' data-title='%s' href='%d/school_detail_view'><i class='icon-eye-open'></i>More Details</a>
                </li>
              </ul>
            </div>
        """ %(obj.id, obj.name, obj.id))
    
    def school_detail_view_link(self, obj):
        return format_html("<a href='%d/school_detail_view' data-toggle='modal' class='modal-click' data-target='.full-content-slider', data-title='%s'>%s</a>" % (obj.id, obj.name, obj.code))
    
    
    def get_queryset(self, request):
        qs = super(SchoolAdmin, self).get_queryset(request)
        return qs.filter(id = request.user.school.id) if request.user.school else qs
        
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            re_path(r'^(.+)/school_detail_view/$', self.school_detail_view, name='%s_%s_school_detail_view' % info),
        ]

        super_urls = super(SchoolAdmin, self).get_urls()

        return my_urls + super_urls

    def school_detail_view(self, request, school_id, form_url='', extra_context=None):
        from django import forms
        from django.shortcuts import get_object_or_404
        opts = School._meta
                
        try:
            shool_details = get_object_or_404(School, pk=school_id)
        except School.DoesNotExist:
            shool_details = None
        
        context = {
            'title': 'School Details : %s' % shool_details,
            'has_change_permission': self.has_change_permission(request, shool_details),
            'opts': opts,
            'app_label': opts.app_label,
            'shool_details': shool_details,
        }
        context.update(extra_context or {})

        return render(request, 'school_detail_view.html', context)
        
    def response_add(self, request, obj):    
        request.session['administrator_school_id'] = obj.id    
        messages.success(request, 'Kindly Proceed to add a default school administrator account for %s' %obj.name)
        return HttpResponseRedirect("/admin/app_core/user/add/")
        
class ClassAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['name', 'numeric_name', 'description', 'teacher', 'date_created']
        })
    ]   
    
    list_display = ('name', 'numeric_name', 'description', 'teacher', 'date_created')
        
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'teacher': 
            kwargs['queryset'] = get_school_teachers(request)
        return super(ClassAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
    
    def get_queryset(self, request):
        qs = super(ClassAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.save()
        
    def get_sections(self, obj):
        return " | ".join([s.name for s in obj.sections.all()])
    get_sections.short_description = 'Sections'
    get_sections.allow_tags = True
    
    def get_subjects(self, obj):
        return " | ".join([s.name for s in obj.subjects.all()])
    get_subjects.short_description = 'Subjects'
    get_subjects.allow_tags = True
    
class SectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['name', 'description', 'date_created']
        })
    ]   
    
    list_display = ('name', 'description', 'date_created')
    search_fields = ('name', 'description', 'date_created') 
    
    def get_queryset(self, request):
        qs = super(SectionAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.save()
        
class SubjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['short_name', 'name', 'date_created']
        })
    ]   
    
    list_display = ('short_name', 'name', 'date_created')
    search_fields = ('short_name', 'name', 'date_created') 
    
    def get_queryset(self, request):
        qs = super(SubjectAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.save()
        
class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = '__all__'
        widgets = {'school': forms.HiddenInput()}
        
class AcademicYearAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['numeric_year', 'description', 'currently_active', 'school']
        })
    ]
    
    list_display = ('numeric_year', 'description', 'school', 'currently_active')
    
    list_filter = ('numeric_year',)
    
    form = AcademicYearForm
    
    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        
        urls = [
            #path(r'^(.+)/send_results/$', self.send_results, name='%s_%s_send_results' % info),
        ]

        super_urls = super(AcademicYearAdmin, self).get_urls()

        return urls + super_urls
        
    def send_results(self, request, year_id, form_url='', extra_context=None):
        try:
            year_details = get_object_or_404(AcademicYear, pk=year_id)
        except AcademicYear.DoesNotExist:
            year_details = None
         
        if year_details and year_details.send_results == 0:
            year_details.send_results = 1 #  0 to 1 queues a year for results sending then 2 marks as sent
            year_details.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    def get_queryset(self, request):
        qs = super(AcademicYearAdmin, self).get_queryset(request)
        return qs.filter(school = request.user.school)
        
    def save_model(self, request, obj, form, change):
    
        if obj.currently_active:
            AcademicYear.objects.filter(school = request.user.school).update(currently_active= False)

        obj.school = request.user.school
        obj.save()
        
        #current_year = datetime.date.today().year
        #AcademicYear.objects.filter(school = request.user.school, numeric_year=current_year).update(currently_active= True)
        
    def get_changeform_initial_data(self, request):
        return {'school': request.user.school}
        
class ClassSubjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['school_class', 'section', 'teacher', 'subject', 'academic_year']
        })
    ]   
    
    list_display = ('school_class', 'section', 'teacher', 'subject', 'academic_year')
    
    list_filter = (ClassesListFilter, SectionListFilter, TeachersListFilter, SubjectsListFilter, AcademicYearListFilter)
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'teacher': 
            kwargs['queryset'] = get_school_teachers(request)
        if db_field.name == 'subject': 
            kwargs['queryset'] = get_school_subjects(request)
        if db_field.name == 'school_class': 
            kwargs['queryset'] = get_school_classes(request)
        if db_field.name == 'section': 
            kwargs['queryset'] = get_school_sections(request)
        if db_field.name == 'academic_year': 
            kwargs['queryset'] = get_school_academic_years(request)
        return super(ClassSubjectAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
        
        
    def get_queryset(self, request):
        qs = super(ClassSubjectAdmin, self).get_queryset(request)
        qs = qs.filter(school_class__school = request.user.school)
        
        section_id = request.GET.get('section_id')
        class_id = request.GET.get('class_id')
        teacher_id = request.GET.get('teacher_id')
        subject_id = request.GET.get('subject_id')
        academic_year_id = request.GET.get('academic_year_id')
                
        if section_id:
            qs = qs.filter(section_id = section_id)
        if class_id:
            qs = qs.filter(school_class_id = class_id)
        if teacher_id:
            qs = qs.filter(teacher_id = teacher_id)
            
        if subject_id:
            qs = qs.filter(subject_id = subject_id)
        if academic_year_id:
            qs = qs.filter(academic_year_id = academic_year_id)
            
        return qs
        


class SyllabusAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['syllabus_class', 'subject']
        })
    ]   
    
    list_display = ('syllabus_class', 'subject', 'view_syllabus')
    list_filter = (ClassesListFilter, SubjectsListFilter)
    search_fields = ('syllabus_class__name', 'subject__name') 
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'syllabus_class': 
            kwargs['queryset'] = get_school_classes(request)
        if db_field.name == 'subject': 
            kwargs['queryset'] = get_school_subjects(request)
        return super(SyllabusAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
    
    def view_syllabus(self, obj):
        return format_html("<a class='btn btn-default' href='../syllabustopic/?q=&class_id=%s&subject_id=%s'><i class='icon-th'></i> View Syllabus</a>" % (obj.syllabus_class.id, obj.subject.id))
    
    def syllabus_detail_view_link(self, obj):
        return format_html("<a href='../syllabustopic/?q=&subject_id=%s'>%s</a>" % (obj.subject.id, obj.syllabus_class))

    
    """inlines = (
        SyllabusTopicsInline,
    )"""
    
    def get_queryset(self, request):
        qs = super(SyllabusAdmin, self).get_queryset(request)
        
        class_id = request.GET.get('class_id')
        subject_id = request.GET.get('subject_id')
        
        qs = qs.filter(subject_id = subject_id) if subject_id else qs
        qs = qs.filter(syllabus_class = class_id) if class_id else qs
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.save()
        
    def response_add(self, request, obj):
        return HttpResponseRedirect("/admin/school/syllabustopic/?q=&class_id=%s&subject_id=%s" %(obj.syllabus_class.id, obj.subject.id))
        
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            re_path(r'^(.+)/view_class_syllabus/$', self.view_class_syllabus, name='%s_%s_view_class_syllabus' % info),
        ]

        super_urls = super(ParentAdmin, self).get_urls()

        return my_urls + super_urls
           
admin.site.register(School, SchoolAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ClassSubject, ClassSubjectAdmin)
admin.site.register(AcademicYear, AcademicYearAdmin)
