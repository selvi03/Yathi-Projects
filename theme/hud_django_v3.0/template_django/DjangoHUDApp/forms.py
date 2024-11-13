from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import OrganizationDataAlt
from .models import TrainingData
from .models import CorporateTraining
from .models import PlacementTraining

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class OrganizationDataForm(forms.ModelForm):
    class Meta:
        model = OrganizationDataAlt
        fields = [
            'org_name', 'spoc_name', 'designation', 'phone_no', 'email', 
            'address', 'location', 'website', 'source_data', 'status', 
            'feedback', 'remark', 'reference','callback_date','initiated_date','followup_date'
        ]
        widgets = {
            'callback_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'initiated_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'followup_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class PlacementTrainingForm(forms.ModelForm):
    class Meta:
        model = PlacementTraining
        fields = [
            'org_name', 'spoc_name', 'designation', 'phone_no', 'email', 
            'address', 'location', 'website', 'source_data', 'status', 
            'feedback', 'remark', 'reference','callback_date','initiated_date','followup_date'
        ]
        widgets = {
            'callback_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'initiated_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'followup_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }   

class TrainingDataForm(forms.ModelForm):
    class Meta:
        model = TrainingData
        fields = ['training_name', 'trainer_name', 'date', 'duration', 'location', 'feedback', 'remarks', 'reference']

        widgets = {
    'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',
        'placeholder': 'Select a date',
    }),
    'duration': forms.TimeInput(attrs={
        'type': 'time',
        'class': 'form-control',
        'placeholder': 'Select a duration',
    }),
}
        


class CorporateTrainingForm(forms.ModelForm):
    class Meta:
        model = CorporateTraining
        fields = ['course_name', 'trainer_name', 'date', 'duration', 'location', 'participants_count', 'cost', 'feedback']

        widgets = {
    'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',
        'placeholder': 'Select a date',
    }),
    'duration': forms.TimeInput(attrs={
        'type': 'time',
        'class': 'form-control',
        'placeholder': 'Select a duration',
    }),
}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'email', 'password', 'gender', 'birth_date', 'mobile_number', 'college_name',
            'id_number', 'batch_number', 'city', 'address', 'state', 'country', 'qualification',
            'experience', 'language', 'skills', 'locations', 'bank_name', 'branch_name', 'ifsc_code',
            'account_number', 'pan_number', 'gst_number', 'photo', 'certificate', 'resume', 'ready_to_relocate'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter address'}),
            # Add more widgets if needed
        }

    def clean_password(self):
        # Hash the password before saving
        password = self.cleaned_data['password']
        # You can hash it using Django's make_password function, e.g.:
        # from django.contrib.auth.hashers import make_password
        # return make_password(password)
        return password  # Make sure to hash it if needed, or use Django's built-in password hashing
