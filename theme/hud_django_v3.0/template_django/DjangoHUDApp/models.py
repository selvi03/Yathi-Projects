from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class OrganizationDataAlt(models.Model):
    SOURCE_DATA_CHOICES = [
        ('Referral', 'Referral'),
        ('Advertisement', 'Advertisement'),
        ('Social Media', 'Social Media'),
    ]

    STATUS_CHOICES = [
        ('no_response', 'NO response'),
        ('wrong_response', 'Wrong response'),
        ('callback', 'Callback'),
        ('initiated', 'Initiated'),
        ('follow_up', 'Follow Up'),
        ('demo', 'Demo'),
        ('closure', 'Closure'),
    ]

    FEEDBACK_CHOICES = [
        ('Not Interested', 'Not Interested'),
        ('Schedule', 'Schedule'),
        ('Fixed Appointment', 'Fixed Appointment'),
        ('Presentation', 'Presentation'),
        ('Presentation Completed', 'Presentation Completed'),
        ('MOU', 'MOU'),
        ('Trainee', 'Trainee'),
        ('Closure', 'Closure'),
    ]

    org_name = models.CharField(max_length=255)
    spoc_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=10,unique=True, validators=[RegexValidator(r'^[6-9]\d{9}$', 'Phone number must be 10 digits and start with 6, 7, 8, or 9.')])
    email = models.EmailField(unique=True)
    address = models.TextField()
    location = models.CharField(max_length=255)
    website = models.URLField()
    source_data = models.CharField(max_length=255, choices=SOURCE_DATA_CHOICES)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    feedback = models.CharField(max_length=255, choices=FEEDBACK_CHOICES)
    remark = models.TextField()
    reference = models.TextField()
    callback_date = models.DateTimeField(null=True, blank=True)
    initiated_date = models.DateTimeField(null=True, blank=True)
    followup_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        print(f'Saving OrganizationDataAlt: {self.__dict__}')  # Print the instance data
        super().save(*args, **kwargs)

    def __str__(self):
        return self.status
    
class PlacementTraining(models.Model):
    SOURCE_DATA_CHOICES = [
        ('Referral', 'Referral'),
        ('Advertisement', 'Advertisement'),
        ('Social Media', 'Social Media'),
    ]

    STATUS_CHOICES = [
        ('no_response', 'NO response'),
        ('wrong_response', 'Wrong response'),
        ('callback', 'Callback'),
        ('initiated', 'Initiated'),
        ('follow_up', 'Follow Up'),
        ('demo', 'Demo'),
        ('closure', 'Closure'),
    ]

    FEEDBACK_CHOICES = [
        ('Not Interested', 'Not Interested'),
        ('Schedule', 'Schedule'),
        ('Fixed Appointment', 'Fixed Appointment'),
        ('Presentation', 'Presentation'),
        ('Presentation Completed', 'Presentation Completed'),
        ('MOU', 'MOU'),
        ('Trainee', 'Trainee'),
        ('Closure', 'Closure'),
    ]

    org_name = models.CharField(max_length=255)
    spoc_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=10, validators=[RegexValidator(r'^[6-9]\d{9}$', 'Phone number must be 10 digits and start with 6, 7, 8, or 9.')],unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField()
    location = models.CharField(max_length=255)
    website = models.URLField()
    source_data = models.CharField(max_length=255, choices=SOURCE_DATA_CHOICES)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    feedback = models.CharField(max_length=255, choices=FEEDBACK_CHOICES)
    remark = models.TextField()
    reference = models.TextField()
    callback_date = models.DateTimeField(null=True, blank=True)
    initiated_date = models.DateTimeField(null=True, blank=True)
    followup_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.org_name
   

class TrainingData(models.Model):
    FEEDBACK_CHOICES = [
        ('Not Interested', 'Not Interested'),
        ('Schedule', 'Schedule'),
        ('Fixed Appointment', 'Fixed Appointment'),
        ('Presentation', 'Presentation'),
        ('Presentation Completed', 'Presentation Completed'),
        ('MOU', 'MOU'),
        ('Trainee', 'Trainee'),
        ('Closure', 'Closure'),
    ]
    training_name = models.CharField(max_length=255)
    trainer_name = models.CharField(max_length=255)
    date = models.DateField()
    duration = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    feedback = models.TextField(max_length=200, choices=FEEDBACK_CHOICES)
    remarks = models.TextField()
    reference = models.CharField(max_length=255)

    def __str__(self):
        return self.training_name

class CorporateTraining(models.Model):
    FEEDBACK_CHOICES = [
        ('Not Interested', 'Not Interested'),
        ('Schedule', 'Schedule'),
        ('Fixed Appointment', 'Fixed Appointment'),
        ('Presentation', 'Presentation'),
        ('Presentation Completed', 'Presentation Completed'),
        ('MOU', 'MOU'),
        ('Trainee', 'Trainee'),
        ('Closure', 'Closure'),
    ]
    course_name = models.CharField(max_length=200)  # Name of the training
    trainer_name = models.CharField(max_length=200)    # Name of the trainer
    date = models.DateField()                            # Date of the training
    duration = models.DurationField()                    # Duration of the training
    location = models.CharField(max_length=200)         # Location of the training
    participants_count = models.PositiveIntegerField()   # Count of participants
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cost of the training
    feedback = models.TextField(max_length=200, choices=FEEDBACK_CHOICES)             # Feedback from participants

    def __str__(self):
        return self.course_name  # This will be displayed in the admin

class Profile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    country = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    birth_date = models.DateField()

    def __str__(self):
        return self.name

class LoginLogoutEvent(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10)  # 'login' or 'logout'
    event_time = models.DateTimeField(default=timezone.now)  # Time of the event

    def __str__(self):
        return f"{self.profile.name} - {self.event_type} at {self.event_time}"
