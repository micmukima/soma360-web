from django.contrib import admin

from school.models import Class, Section
from school.models import ClassSubject, Subject, AcademicYear
from student.models import StudentPromotion
from app_utils.functions import user_is_teacher

class AcademicYearListFilter(admin.SimpleListFilter):
    title = 'Academic Year'
    parameter_name = 'academic_year_id'

    def lookups(self, request, model_admin):
        qs = AcademicYear.objects.filter(school = request.user.school)
        return set([(related_obj.id, related_obj.numeric_year) for related_obj in qs])
            
    def queryset(self, request, queryset):
        return queryset 
        
class SubjectsListFilter(admin.SimpleListFilter):
    title = 'Subject'
    parameter_name = 'subject_id'

    def lookups(self, request, model_admin):
        unique_sections = []
        qs = Subject.objects.filter(school=request.user.school)
        return set([(related_obj.id, related_obj.name) for related_obj in qs]) 
    def queryset(self, request, queryset):
        return queryset

class SectionListFilter(admin.SimpleListFilter):
    title = 'Section'
    parameter_name = 'section_id'
    def lookups(self, request, model_admin):
        qs = Section.objects.filter(school=request.user.school).order_by('name')         
        return sorted(set([(related_obj.id, related_obj.name) for related_obj in qs]))       
        
    def queryset(self, request, queryset):
        return queryset
        
class ClassesListFilter(admin.SimpleListFilter):
    title = 'Class'
    parameter_name = 'class_id'

    def lookups(self, request, model_admin):
        qs = Class.objects.filter(school=request.user.school).order_by('numeric_name')   
        return sorted(set([(related_obj.id, related_obj.name) for related_obj in qs]))
    def queryset(self, request, queryset):
        return queryset
        
class ClassSubjectSectionListFilter(admin.SimpleListFilter):
    title = 'Section'
    parameter_name = 'section_id'

    def lookups(self, request, model_admin):
        unique_sections = []
        
        if user_is_teacher(request.user):
            qs = ClassSubject.objects.filter(school_class__school=request.user.school, teacher=request.user)
            return set([(related_obj.section.id, related_obj.section.name) for related_obj in qs])
        else:
            qs = Section.objects.filter(school=request.user.school).order_by('name')
            return sorted(set([(related_obj.id, related_obj.name) for related_obj in qs]))
        
    def queryset(self, request, queryset):
        return queryset
        
class PromotionFromClassesListFilter(admin.SimpleListFilter):
    title = 'From Class'
    parameter_name = 'from_class_id'

    def lookups(self, request, model_admin):
        qs = StudentPromotion.objects.filter(student__school=request.user.school)
        return set([(related_obj.from_class.id, related_obj.from_class.name) for related_obj in qs])
    def queryset(self, request, queryset):
        return queryset
        
    
class PromotionToClassesListFilter(admin.SimpleListFilter):
    title = 'To Class'
    parameter_name = 'to_class_id'

    def lookups(self, request, model_admin):
        qs = StudentPromotion.objects.filter(student__school=request.user.school)
        return set([(related_obj.to_class.id, related_obj.to_class.name) for related_obj in qs])
    def queryset(self, request, queryset):
        return queryset
        
class ClassSubjectClassesListFilter(admin.SimpleListFilter):
    title = 'Class'
    parameter_name = 'class_id'

    def lookups(self, request, model_admin):

        if user_is_teacher(request.user):
            qs = ClassSubject.objects.filter(school_class__school=request.user.school, teacher=request.user)
            return sorted(set([(related_obj.school_class.id, related_obj.school_class.name) for related_obj in qs]))
        else:        
            qs = Class.objects.filter(school=request.user.school).order_by('numeric_name')   
            return sorted(set([(related_obj.id, related_obj.name) for related_obj in qs]))
    def queryset(self, request, queryset):
        return queryset
