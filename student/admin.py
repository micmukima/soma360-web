import csv
from .models import *
from django.urls import path
from django import forms
from django.contrib import admin

from app_utils.select_lists import *

from django.contrib import messages
from django.shortcuts import render
from app_core import parser as post_parser

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from app_utils.functions import clean_mobile_number

from school.models import Class

from .forms import BatchUploadForm
from school.models import ClassSubject
from django.contrib.auth.models import Group
from app_utils.list_filters import SectionListFilter, \
    ClassesListFilter, ClassesListFilter, SectionListFilter, \
    PromotionFromClassesListFilter, PromotionToClassesListFilter, \
    ClassSubjectClassesListFilter, ClassSubjectSectionListFilter, \
    AcademicYearListFilter  

from django.urls import path, re_path

class StudentAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None, {
            'fields': ['firstname', 'middlename', 'lastname', 'parent_1', 
                'parent_2', 'address', 'date_registered', 'current_class', 
                'current_section', 'current_academic_year', 'photo']
        })
    ]   
    
    list_display = ('student_photo_inline', 'student_detail_view_link', 
        'student_names', 'parent_1', 'parent_2', 'current_class', 
        'current_section', 'current_academic_year', 'edit_student_link')
    list_filter = ('date_registered', ClassSubjectClassesListFilter, ClassSubjectSectionListFilter, AcademicYearListFilter)
    search_fields = ('firstname', 'middlename', 'lastname', 'parent_1__firstname', 'parent_1__lastname', 
        'parent_2__firstname', 'parent_2__lastname', 'parent_1__contact_phone', 'parent_2__contact_phone', 
        'address', 'registration_number')
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'current_class': 
            kwargs['queryset'] = get_school_classes(request)
        if db_field.name == 'current_section': 
            kwargs['queryset'] = get_school_sections(request)
        if db_field.name == 'parent_1' or db_field.name == 'parent_2': 
            kwargs['queryset'] = get_school_parents(request)
        if db_field.name == 'current_academic_year':
            kwargs['queryset'] = get_school_academic_years(request)
        return super(StudentAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
        
    def get_queryset(self, request):
        class_id = request.GET.get('class_id')
        section_id = request.GET.get('section_id')
        academic_year_id = request.GET.get('academic_year_id')
        
        qs = super(StudentAdmin, self).get_queryset(request)
        qs = qs.filter(current_class_id = class_id) if class_id else qs
        qs = qs.filter(current_section_id = section_id) if section_id else qs
        qs = qs.filter(current_academic_year = academic_year_id) if academic_year_id else qs
        return qs.filter(school = request.user.school)# if not request.user.is_system_admin else qs
        
    def save_model(self, request, obj, form, change):
        obj.school = request.user.school
        obj.save()
    
    def student_photo_inline(self, obj):
        if obj.photo:
            return render_to_string('thumbnail.html', {
                'photo': obj.photo
            })
    student_photo_inline.short_description = "Photo"
    
    def student_names(self, obj):
        return u"%s %s %s" % (obj.firstname, obj.middlename, obj.lastname)
    student_names.short_description = 'Student Names'
    student_names.allow_tags = True
    
    def edit_student_link(self, obj):
        return """
            <div class='dropdown'>
              <a class='btn btn-default dropdown-toggle' data-toggle='dropdown'>Actions
              <span class='caret'></span></a>
              <ul class='dropdown-menu'>
                <li>
                    <a class='modal-click' data-toggle='modal' data-target='.full-content-slider' data-title='%s %s %s' href='%d/student_grades'><i class='icon-th'></i> View Grades</a>
                </li>
                <li>
                    <a href='%d/'><i class='icon-edit'></i> Edit</a>
                </li>
                <li>
                    <a class='modal-click' data-toggle='modal' data-target='.full-content-slider' data-title='%s %s %s' href='%d/student_detail_view'><i class='icon-eye-open'></i> More Details</a>
                </li>
              </ul>
            </div>
        """ %(obj.firstname, obj.middlename, obj.lastname, obj.id, obj.id, obj.firstname, obj.middlename, obj.lastname, obj.id)
    edit_student_link.short_description = 'Actions'
    edit_student_link.allow_tags = True
    
    def student_detail_view_link(self, obj):
        return u"<a href='%d/student_detail_view' data-toggle='modal' class='modal-click' data-target='.full-content-slider' data-title='%s %s %s'>%s</a>" % (obj.id, obj.firstname, obj.middlename, obj.lastname, obj.registration_number)
    student_detail_view_link.short_description = "Reg. Number"
    student_detail_view_link.allow_tags = True
    
    def get_urls(self):


        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [

            re_path(r'^(.+)/student_detail_view/$', self.student_detail_view, name='%s_%s_student_detail_view' % info),
        ]

        super_urls = super(StudentAdmin, self).get_urls()

        return my_urls + super_urls
        
    def get_score_grade(self, grade_score, grading_scale,  total_marks = None, total_maximum = None):
    
        if not total_marks:
            total_maximum = grade_score.exam.maximum_score
            total_marks = grade_score.score
            
        adjusted_score = (total_marks/float(total_maximum))*100
        for grade_entry in grading_scale:
            if adjusted_score > grade_entry.mark_upto:
                continue
            return grade_entry.grade  
    
        return "-"
        
    def gradebook_per_exam(self, gradebook, grading_scale):
        grades_detailed = {}
        for grade_score in gradebook:
            if grade_score.exam.id not in grades_detailed:
                grades_detailed[grade_score.exam.id] = {
                    'exam_name' : grade_score.exam,
                    'subject_scores' : {},
                    'total_maximum' : 0,
                    'total_marks' : 0,
                    'grade': '-',
                }
            if grade_score.subject.id not in grades_detailed[grade_score.exam.id]['subject_scores']:
                grades_detailed[grade_score.exam.id]['subject_scores'][grade_score.subject.id] = {
                    'subject' : grade_score.subject,
                    'score' : grade_score.score,
                    'maximum_score' : grade_score.exam.maximum_score,
                    'score_grade' : self.get_score_grade(grade_score, grading_scale),
                }
            grades_detailed[grade_score.exam.id]['total_maximum'] += grade_score.exam.maximum_score
            grades_detailed[grade_score.exam.id]['total_marks'] += grade_score.score
            grades_detailed[grade_score.exam.id]['grade'] = \
                self.get_score_grade(grade_score, grading_scale, \
                grades_detailed[grade_score.exam.id]['total_marks'], grades_detailed[grade_score.exam.id]['total_maximum'])
            
        return grades_detailed
        
    def student_grades(self, request, student_id, form_url='', extra_context=None):
        
        opts = Gradebook._meta
        grading_scale = GradingScale.objects.filter(school = request.user.school).order_by('mark_upto')
        try:
            gradebook = Gradebook.objects.filter(student_id=student_id)
        except Gradebook.DoesNotExist:
            gradebook = None
            
        if gradebook:
            gradebook = self.gradebook_per_exam(gradebook, grading_scale)
        
        context = {
            'title': 'Student Gradebook : %s' % gradebook,
            'has_change_permission': self.has_change_permission(request, gradebook),
            'opts': opts,
            'app_label': opts.app_label,
            'gradebook': gradebook,
        }
        context.update(extra_context or {})

        return render(request, 'student_grades_view.html', context)

    def student_detail_view(self, request, student_id, form_url='', extra_context=None):
        
        opts = Parent._meta
                
        try:
            student_details = get_object_or_404(Student, pk=student_id)
        except Student.DoesNotExist:
            student_details = None
        
        context = {
            'title': 'Student Details : %s' % student_details,
            'has_change_permission': self.has_change_permission(request, student_details),
            'opts': opts,
            'app_label': opts.app_label,
            'student_details': student_details,
        }
        context.update(extra_context or {})

        return render(request, 'student_detail_view.html', context)
        
class StudentPromotionAdmin(admin.ModelAdmin): 
    fieldsets = [
        (None, {
            'fields': ['student', 'from_class', 'to_class']
        })
    ]   
    
    list_display = ('student', 'from_class', 'to_class', 'from_section', 'to_section', 'from_academic_year', 'to_academic_year', 'promoted_by', 'date_promoted')
    list_filter = (PromotionFromClassesListFilter, PromotionToClassesListFilter, 'date_promoted')
    search_fields = ('student__firstname', 'student__middlename', 'student__lastname', \
        'from_class__name', 'to_class__name', 'from_academic_year__numeric_year', 'to_academic_year__numeric_year', 'from_section__name', 'to_section__name') 
    
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        
        urls = [
            #path(r'^promote/$', self.promote_students, name='%s_%s_promote' % info),
        ]

        super_urls = super(StudentPromotionAdmin, self).get_urls()

        return urls + super_urls
        
    def promote_students(self, request, form_url='', extra_context=None):
        opts = Student._meta     
        from tal_utils.functions import user_is_teacher
        class_sections = ClassSubject.objects.filter(school_class__school = request.user.school)
        
        classes = {}
        sections = {}
        
        all_classes = get_school_classes(request)
        all_sections = get_school_sections(request)
        
        if user_is_teacher(request.user):
            class_sections = class_sections.filter(teacher=request.user)
            # teacher can only promote withis allocated assignments
            for cs in class_sections:
                classes[cs.school_class.id] = cs.school_class.name
                sections[cs.section.id] = cs.section.name
        else:
            for cs in all_classes:
                classes[cs.id] = cs.name
            for sec in all_sections:
                sections[sec.id] = sec.name
        
        academic_years = get_school_academic_years(request) 
          
        try:
            current_section = request.POST.get('current_section')
            current_class = request.POST.get('current_class')  
            current_academic_year = request.POST.get('current_academic_year')
            students = Student.objects.filter(school = request.user.school, current_class_id = current_class, current_section_id = current_section, current_academic_year = current_academic_year)
            """if current_section:
                students = students.filter(current_section_id = current_section) """
        except Student.DoesNotExist:
            students = None
            
        if request.method == "POST":  
            promote_to_class = request.POST.get('promote_to_class')
            promote_to_section = request.POST.get('promote_to_section')
            promote_to_academic_year = request.POST.get('promote_to_academic_year')          
            if promote_to_class:
                post_dict = post_parser.parse(request.POST.urlencode())   
                if 'selected_student' in post_dict:
                    selected_students = post_dict['selected_student']
                    if not type(selected_students) is list:
                        selected_students = [post_dict['selected_student']]

                    for student_id in selected_students:
                        promote_student = Student.objects.filter(pk = student_id).first()
                        if not promote_to_section:
                            promote_to_section = promote_student.current_section_id
                        if promote_student:
                            sp = StudentPromotion(
                                student = promote_student,
                                from_class_id = promote_student.current_class_id,
                                to_class_id = promote_to_class,
                                from_section_id = promote_student.current_section_id,
                                to_section_id = promote_to_section,
                                promoted_by = request.user,
                                from_academic_year_id = current_academic_year,
                                to_academic_year_id = promote_to_academic_year
                            )
                            sp.save()
                            promote_student.current_class_id = promote_to_class
                            promote_student.current_academic_year_id = promote_to_academic_year
                            promote_student.current_section_id = promote_to_section
                            promote_student.save()
                    messages.success(request, "Student promotion successful.")
                            
        context = {
            'title': 'Promote Students',
            'opts': opts,
            'app_label': opts.app_label,
            'students': students,
            'classes'  : classes,
            'sections' : sections,
            'all_classes' : all_classes,
            'all_sections' : all_sections,
            'academic_years' : academic_years,
            'current_section' : int(current_section) if current_section else '', # prepare for compare with int in tremplate if statement
            'current_class' : int(current_class) if current_class else '',
            'current_academic_year' : int(current_academic_year) if current_academic_year else '',
            
        }
        context.update(extra_context or {})
        return render(request, 'student_promition.html', context)
    
    def get_queryset(self, request):
        qs = super(StudentPromotionAdmin, self).get_queryset(request)
        qs = qs.filter(student__school = request.user.school)
        
        from_class_id = request.GET.get('from_class_id')
        to_class_id = request.GET.get('to_class_id')
        if from_class_id:
            qs = qs.filter(from_class_id = from_class_id)
        if to_class_id:
            qs = qs.filter(to_class_id = to_class_id)
        return qs
        
        """qs = super(ExamAdmin, self).get_queryset(request)
        qs = qs.filter(school = request.user.school)
        term_id = request.GET.get('term_id')
        return qs.filter(term_id = term_id) if term_id else qs"""
    def save_model(self, request, obj, form, change):
        obj.student.current_class = obj.to_class
        obj.promoted_by = request.user
        obj.save()
        obj.student.save()
        
class StudentBulkAdmitAdmin(admin.ModelAdmin): 

    form = BatchUploadForm
        
    list_display = ('firstname', 'middlename', 'lastname', 'parent_1', 'current_class', 'current_section')
        
    list_filter = (ClassesListFilter, SectionListFilter)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(StudentBulkAdmitAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['current_class'].queryset = get_school_classes(request)
        form.base_fields['current_section'].queryset = get_school_sections(request)
        form.base_fields['current_academic_year'].queryset = get_school_academic_years(request)
        form.base_fields['current_academic_year'].initial = get_school_current_academic_year(request)
        return form
        
    def get_queryset(self, request):        
        class_id = request.GET.get('class_id')
        section_id = request.GET.get('section_id')        
        qs = super(StudentBulkAdmitAdmin, self).get_queryset(request)
        qs = qs.filter(current_class_id = class_id) if class_id else qs
        qs = qs.filter(current_section_id = section_id) if section_id else qs
        
        return qs.filter(school = request.user.school)
        
    def save_model(self, request, obj, form, change): 
        if request.method == "POST":
            form = BatchUploadForm(request.POST, request.FILES)
            if form.is_valid():           
                file = request.FILES['batchFile']
                reader = csv.DictReader( file )
                current_class = form.cleaned_data['current_class']
                current_section = form.cleaned_data['current_section']
                current_academic_year = form.cleaned_data['current_academic_year']
                parent_group = Group.objects.get(name='Parent')
                for conter, line in enumerate(reader, 1):                    
                    parent_1, created = Parent.objects.get_or_create(
                        firstname = line['Parent 1 First Name'],
                        lastname = line['Parent 1 Last Name'],
                        contact_phone = clean_mobile_number(line['Parent 1 Mobile Number']),
                        username = clean_mobile_number(line['Parent 1 Mobile Number']),
                        school = request.user.school,                        
                    )
                    if created:                        
                        parent_1.groups.add(parent_group)
                                        
                    parent_2, created = Parent.objects.get_or_create(
                        firstname = line['Parent 2 First Name'],
                        lastname = line['Parent 2 Last Name'],
                        contact_phone = clean_mobile_number(line['Parent 2 Mobile Number']),
                        username = clean_mobile_number(line['Parent 2 Mobile Number']),
                        school = request.user.school,                        
                    )
                    if created:                        
                        parent_2.groups.add(parent_group)
                      
                    student, created = Student.objects.get_or_create(
                        school = request.user.school,                        
                        firstname = line['First Name'],
                        middlename = line['Middle Name'],
                        lastname = line['Last Name'],
                        address = line['Address'],
                        current_class = current_class,
                        current_section = current_section,
                        current_academic_year = current_academic_year,
                        parent_1 = parent_1,
                        parent_2 = parent_2,                        
                    )
            # suppress default success message, then after sending a warning - use tha extra_tags to display in success green colors
            messages.set_level(request, messages.WARNING)
            messages.warning(request, "Bulk student admit successful.", extra_tags='success')
        super(StudentBulkAdmitAdmin, self)

admin.site.register(Student, StudentAdmin)
admin.site.register(StudentPromotion, StudentPromotionAdmin)
admin.site.register(StudentBulkAdmit, StudentBulkAdmitAdmin)
