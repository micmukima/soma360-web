from django import forms
from core.models import User

class RegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    #email = forms.EmailField(widget=forms.widget.TextInput,label="Email")
    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=True)    
    mobile_number = forms.CharField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['mobile_number', 'firstname', 'lastname', 'mobile_number', 'password1', 'password2', 'username']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

