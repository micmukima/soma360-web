from teacher.models import Teacher
from school.models import Subject, Class, Section, AcademicYear
from school.models import SchoolTerm
from parent.models import Parent
from student.models import Student

def get_school_teachers(request):
    return Teacher.objects.filter(school = request.user.school)
    
def get_school_subjects(request):
    return Subject.objects.filter(school = request.user.school)
    
def get_school_students(request):
    return Student.objects.filter(school = request.user.school)
    
    
def get_school_classes(request):
    return Class.objects.filter(school = request.user.school)
    
def get_school_sections(request):
    return Section.objects.filter(school = request.user.school)

    
def get_school_academic_years(request):
    return AcademicYear.objects.filter(school = request.user.school)
    
def get_school_current_academic_year(request):
    return AcademicYear.objects.filter(school = request.user.school, currently_active = True).first()
    
def get_school_terms(request):
    return SchoolTerm.objects.filter(school = request.user.school)
    
def get_school_parents(request):
    return Parent.objects.filter(school = request.user.school)
        
