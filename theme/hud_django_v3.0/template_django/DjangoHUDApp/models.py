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
    gender = models.CharField(max_length=10)
    birth_date = models.DateField()
    mobile_number = models.CharField(max_length=15)
    college_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=50)
    batch_number = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.TextField()
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    qualification = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()
    language = models.CharField(max_length=20)
    skills = models.CharField(max_length=20)
    locations = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=20)
    gst_number = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    ready_to_relocate = models.BooleanField(default=False)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('$'):  # Hash password if it's plain text
            self.password = make_password(self.password)
        super(Profile, self).save(*args, **kwargs)



class LoginLogoutEvent(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10)  # 'login' or 'logout'
    event_time = models.DateTimeField(default=timezone.now)  # Time of the event

    def __str__(self):
        return f"{self.profile.name} - {self.event_type} at {self.event_time}"
