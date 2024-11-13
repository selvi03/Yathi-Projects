from django.contrib import admin
from .models import Profile, LoginLogoutEvent
from .models import OrganizationDataAlt
from .models import TrainingData
from .models import CorporateTraining
from .models import PlacementTraining

@admin.register(OrganizationDataAlt)
class OrganizationDataAltAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'spoc_name', 'designation', 'phone_no', 'email', 'address', 'location', 'website', 'source_data', 'status', 'feedback', 'remark', 'reference','callback_date','initiated_date','followup_date')
    search_fields = ('org_name', 'spoc_name', 'email')
    list_filter = ('status', 'source_data')

@admin.register(PlacementTraining)
class PlacementTrainingAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'spoc_name', 'designation', 'phone_no', 'email', 'address', 'location', 'website', 'source_data', 'status', 'feedback', 'remark', 'reference','callback_date','initiated_date','followup_date')
    search_fields = ('org_name', 'spoc_name', 'email')
    list_filter = ('status', 'source_data')

@admin.register(TrainingData)  # Register the TrainingData model
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ('training_name', 'trainer_name', 'date', 'duration', 'location', 'feedback', 'remarks', 'reference')  # Replace with actual fields from TrainingData
    search_fields = ('training_name', 'trainer_name')  # Replace with fields you want to search
    list_filter = ('date','location')  # Replace with fields you want to filter

@admin.register(CorporateTraining)
class CorporateTrainingAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'trainer_name', 'date', 'duration', 'location', 'participants_count', 'cost','feedback')  # New fields
    search_fields = ('course_name', 'trainer_name')  # Fields to search
    list_filter = ('date', 'location')  # Fields to filter

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'name', 'email', 'gender', 'birth_date', 'mobile_number', 'college_name', 
        'id_number', 'batch_number', 'city', 'state', 'country', 'qualification', 
        'experience', 'language', 'skills', 'locations', 'bank_name', 'branch_name', 
        'ifsc_code', 'account_number', 'pan_number', 'gst_number', 'ready_to_relocate'
    )
    
    search_fields = ('name', 'email', 'college_name', 'mobile_number', 'city', 'state', 'country', 'skills')
    list_filter = ('gender', 'country', 'qualification', 'ready_to_relocate', 'language', 'skills')
    ordering = ('name',)  # You can change to '-name' for reverse order if needed
    readonly_fields = ('photo', 'certificate', 'resume')  # Only if you want to prevent editing these fields

@admin.register(LoginLogoutEvent)
class LoginLogoutEventAdmin(admin.ModelAdmin):
    list_display = ('profile', 'event_type', 'event_time')  # Display fields
    list_filter = ('event_type', 'event_time')  # Filter by event type and time
    search_fields = ('profile__name', 'profile__email')  # Search by profile name or email
    ordering = ('-event_time',)  # Order by event time, most recent first

