from django import forms

from django.contrib.admin import widgets
from django.utils import timezone
from school.models import Class,Section
from .models import StudentBulkAdmit
from django.core.exceptions import ValidationError
import csv

class BatchUploadForm(forms.ModelForm):
    batchFile = forms.FileField(label='Select a bulky CSV file to import students:', required=True)
    current_class = forms.ModelChoiceField(queryset=None)
    current_section = forms.ModelChoiceField(queryset=None)
    current_academic_year = forms.ModelChoiceField(queryset=None)
    
    def clean_batchFile(self):
        csv_required_keys = ['First Name','Middle Name','Last Name','Address','Parent 1 First Name','Parent 1 Last Name','Parent 1 Mobile Number','Parent 2 First Name','Parent 2 Last Name','Parent 2 Mobile Number']   
        file = self.cleaned_data.get("batchFile", False)
        reader = csv.DictReader( file )
        error_message = ""

        lr_diff = lambda l, r: list(set(l).difference(r))
        #lr_intr = lambda l, r: list(set(l).intersection(r))
        #lr_symm = lambda l, r: list(set(l).symmetric_difference(r))
        #lr_cont = lambda l, r: set(l).issuperset(r)  
        #lr_union = lambda l, r: list(set(l).union(r))
        missing_columns = lr_diff(csv_required_keys, reader.fieldnames) #list(set(line.keys()) - set(csv_required_keys))
        
        if len(missing_columns):
            error_string = ''
            for mi in missing_columns:
                error_string = "%s [ %s ]" %(error_string, mi)
            error_message = "Upload file missing required information : %s" %(error_string)                     
            raise ValidationError(error_message)
        return file
    
    class Meta:
        model = StudentBulkAdmit
        fields = ['current_class', 'current_section', 'current_academic_year', 'batchFile']
