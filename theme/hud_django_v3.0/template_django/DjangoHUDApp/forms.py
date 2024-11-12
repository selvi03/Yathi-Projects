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
    birth_month = forms.ChoiceField(choices=[('01', 'Jan'), ('02', 'Feb')], required=True)
    birth_day = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1, 32)], required=True)
    birth_year = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1980, 2025)], required=True)

    class Meta:
        model = Profile
        fields = ['name', 'email', 'password', 'country', 'gender']

    def clean(self):
        cleaned_data = super().clean()
        birth_date = f"{cleaned_data.get('birth_year')}-{cleaned_data.get('birth_month')}-{cleaned_data.get('birth_day')}"
        cleaned_data['birth_date'] = birth_date
        return cleaned_data
