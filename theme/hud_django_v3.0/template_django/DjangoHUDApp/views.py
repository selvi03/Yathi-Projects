from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse
from google.oauth2.service_account import Credentials

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import OrganizationDataAlt
from .forms import OrganizationDataForm
from .models import TrainingData
from .forms import TrainingDataForm
from .models import CorporateTraining
from .forms import CorporateTrainingForm
from .models import PlacementTraining
from .forms import PlacementTrainingForm
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from oauth2client.service_account import ServiceAccountCredentials
import logging
from .models import Profile
from datetime import datetime,date,time
# from .google_sheets import append_data_to_sheet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime
from .models import Profile, LoginLogoutEvent
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse, HttpResponse
from django.contrib.sessions.models import Session
import json
import jwt
from django.conf import settings
from django.conf import settings as django_settings
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from .forms import ProfileForm 
from django.http import JsonResponse
import datetime
import json




# Function to generate JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_sheet_data():
    SERVICE_ACCOUNT_FILE = 'E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
    
    # The ID of the Google Spreadsheet and range
    SPREADSHEET_ID = '1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE'
    RANGE_NAME = 'profile!A:Z'

    # Define the scope
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Load the credentials
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Google Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Read data from the sheet
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values  # Returns all rows of data from the sheet




def pageLogin(request):
    context = {
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0'
    }

    if request.method == 'GET':
        if request.session.get('email'):
            return redirect('DjangoHUDApp:landing')  # Redirect to the landing page after login
        return render(request, 'pages/page-login.html', context)

    elif request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required.'}, status=400)
            
            sheet_data = get_sheet_data()
            print(sheet_data)

            for row in sheet_data[1:]:  # Skip header row
                if email.strip() == row[1].strip() and password.strip() == row[2].strip():
                    role = row[14].strip()
                    print(f"Retrieved role for {email}: {role}")  # Debug: Print the role

                    token_payload = {
                        'email': email,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                        'iat': datetime.datetime.utcnow(),
                    }
                    token = jwt.encode(token_payload, django_settings.SECRET_KEY, algorithm='HS256')
                    print(token)
                    request.session['email'] = email
                    request.session['jwt_token'] = token

                    append_or_update_sheet(
                        email=email,
                        event_type='Login',
                        spreadsheet_id='1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE',
                        range_name='login!A:E',
                        service_account_file='E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
                    )
                    # Redirect based on role
                    if role.strip().lower() == 'admin':
                        print(f"Redirecting {email} to organization-data-list")  
                        return redirect('DjangoHUDApp:organization-data-list')
                    elif role.strip().lower() == 'manager':
                        print(f"redirecting {email} to placement_training")
                        return redirect('DjangoHUDApp:placement_training')
                    elif role.strip().lower() == 'user':
                        print(f"redirecting {email} to training_data")
                        return redirect('DjangoHUDApp:training_data')
                    elif role.strip().lower() == 'trainer':
                        print(f"redirecting {email} to corporate_training")
                        return redirect('DjangoHUDApp:corporate_training')
                    else:
                        print(f"Redirecting {email} to landing")  
                        return redirect('DjangoHUDApp:landing')

                    # return redirect('DjangoHUDApp:landing')  # Redirect to authenticated page
            return JsonResponse({'error': 'Invalid credentials.'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def log_inactivity(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            logout_time = data.get('logout_time')  # Inactivity logout time
            auto_logout = data.get('auto_logout', False)

            # Ensure the user is authenticated before logging the inactivity event
            if request.session.get('email'):  # Check if the user is logged in
                email = request.session.get('email')
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Log the inactivity event in the Google Sheet
                append_or_update_sheet(
                    email=email,
                    event_type='Auto Logout' if auto_logout else 'Logout',
                    spreadsheet_id='1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE',
                    range_name='login!A:E',
                    service_account_file='E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
                )

                return JsonResponse({'status': 'success', 'message': 'Inactivity logged.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'User not logged in.'}, status=401)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)





@csrf_exempt
def logout(request):
    if not request.session.get('email'):  # Check if the user is logged in
        # Redirect to the login page if no session exists
        return redirect('DjangoHUDApp:pageLogin')

    if request.method in ['POST', 'GET']:
        try:
            email = request.session.get('email', 'Unknown')  # Get email from the session

            # Log the logout event in Google Sheets
            append_or_update_sheet(
                email=email,
                event_type='Logout',
                spreadsheet_id='1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE',
                range_name='login!A:E',
                service_account_file='E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
            )

            # Clear the session (logout the user)
            request.session.flush()
            return redirect('DjangoHUDApp:pageLogin')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def append_or_update_sheet(email, event_type, spreadsheet_id, range_name, service_account_file):
    """
    Append or update a row in the Google Sheet based on the event type (login/logout).
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if event_type == 'Login':
        # Append a new row for login with empty fields for logout and duration
        data = [[email, current_time, '', '', '']]
        body = {'values': data}
        sheet = service.spreadsheets()
        sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

    elif event_type == 'Logout':
        # Find the last login row for the given email
        row_num = find_last_login_row(email, spreadsheet_id, range_name, service_account_file)
        
        if row_num:
            # Get the login time and update the row with logout time and duration
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=f'{range_name}').execute()
            values = result.get('values', [])
            
            if row_num <= len(values):
                # Extract login time
                login_time_str = values[row_num - 1][1]  # Get the login time
                if login_time_str:  # Only proceed if login time exists
                    login_time = datetime.datetime.strptime(login_time_str, '%Y-%m-%d %H:%M:%S')
                    logout_time = datetime.datetime.now()
                    duration = logout_time - login_time  # Duration of the login session

                    # Update the logout time and duration
                    update_body = {
                        'values': [[current_time, str(duration)]]
                    }
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'login!C{row_num}:D{row_num}',  # Update the correct row with logout and duration
                        valueInputOption='RAW',
                        body=update_body
                    ).execute()

        else:
            # If no login record was found, create a new entry with login and logout time
            data = [[email, current_time, '', '', '']]
            body = {'values': data}
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()


def find_last_login_row(email, spreadsheet_id, range_name, service_account_file):
    """
    Find the last login row for the given email.
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Retrieve the spreadsheet data
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    # Look for the last row with the specified email
    for row_num, row in reversed(list(enumerate(values, start=1))):
        if row and row[0] == email and row[1]:  # Ensure there is a login time
            return row_num
    return None










def landing(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/landing.html", context)





def validate_token(request):
    token = request.session.get('jwt_token')
    if token:
        try:
            decoded_token = decode(token, django_settings.SECRET_KEY, algorithms=['HS256'])
            return decoded_token  # Token is valid
        except ExpiredSignatureError:
            request.session.flush()  # Clear expired session
            return None
        except InvalidTokenError:
            return None
    return None







    
logger = logging.getLogger(__name__)

@csrf_protect
def organization_data_list(request):
    # Define fields for form updates
    fields = [
        'org_name', 'spoc_name', 'designation', 'phone_no', 'email',
        'address', 'location', 'website', 'source_data', 'status',
        'feedback', 'remark', 'reference', 'callback_date',
        'initiated_date', 'followup_date'
    ]
    
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Function to convert datetime to string format
    def convert_datetime_to_str(date_obj):
        if isinstance(date_obj, datetime):
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        return date_obj
    
    # Function to retrieve data from Google Sheets
    def get_spreadsheet_data():
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'DjangoHUDApp/credentials/google_credentials.json', scope
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xJGQFFkucEbFjJf8Y05x8OOcFp2e_ZxTz_rtjq7QQ1g/edit?gid=914811941#gid=914811941")
            worksheet = sheet.get_worksheet(0)
            
            # Retrieve all rows in the spreadsheet
            rows = worksheet.get_all_values()
            
            # Convert rows to list of dictionaries if there's a header row
            if rows:
                header = rows[0]  # First row as header
                data = []
                for row in rows[1:]:
                    row_dict = dict(zip(header, row))  # Convert each row to a dictionary
                    
                    # Handle dropdown columns - map the text values to the correct choices
                    if 'source_data' in row_dict:
                        # Check if the value exists in the SOURCE_DATA_CHOICES
                        if row_dict['source_data'] in dict(OrganizationDataAlt.SOURCE_DATA_CHOICES):
                            row_dict['source_data'] = row_dict['source_data']
                        else:
                            row_dict['source_data'] = None  # Default to None if not valid
                            
                    if 'status' in row_dict:
                        # Check if the value exists in the STATUS_CHOICES
                        if row_dict['status'] in dict(OrganizationDataAlt.STATUS_CHOICES):
                            row_dict['status'] = row_dict['status']
                        else:
                            row_dict['status'] = None  # Default to None if not valid
                    
                    if 'feedback' in row_dict:
                        # Check if the value exists in the FEEDBACK_CHOICES
                        if row_dict['feedback'] in dict(OrganizationDataAlt.FEEDBACK_CHOICES):
                            row_dict['feedback'] = row_dict['feedback']
                        else:
                            row_dict['feedback'] = None  # Default to None if not valid
                    
                    # Append the row dictionary to the data list
                    data.append(row_dict)
                return data
            else:
                return []
        except Exception as e:
            logger.error("Error retrieving Google Sheets data: %s", e)
            return []

    # Handle POST request for form submission or field update
    if request.method == 'POST':
        form = OrganizationDataForm(request.POST)
        
        # Handle field update via POST (editing specific fields in an existing entry)
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value')
        instance_id = request.POST.get('instance_id')
        
        if field_name and field_value and instance_id:
            if field_name in fields:
                try:
                    org_data = OrganizationDataAlt.objects.get(id=instance_id)
                    setattr(org_data, field_name, field_value)
                    org_data.save()
                    logger.info(f'Updated {field_name} for instance {instance_id}')
                    return JsonResponse({'success': True})
                except OrganizationDataAlt.DoesNotExist:
                    logger.error('Instance not found for ID: %s', instance_id)
                    return JsonResponse({'success': False, 'message': 'Instance not found'}, status=404)
                except Exception as e:
                    logger.error('Error saving data: %s', str(e))
                    return JsonResponse({'success': False, 'message': str(e)}, status=500)
            else:
                logger.warning('Invalid field name attempted: %s', field_name)
                return JsonResponse({'success': False, 'message': 'Invalid field name'}, status=400)

        # Handle form submission (new entry)
        if form.is_valid():
            try:
                # Save form data to the model
                org_data = form.save(commit=False)
                org_data.save()

                # Convert datetime fields to strings before sending to Google Sheets
                cleaned_data = form.cleaned_data
                for field in ['callback_date', 'initiated_date', 'followup_date']:
                    cleaned_data[field] = convert_datetime_to_str(cleaned_data[field])

                # Load credentials and authorize access to Google Sheets
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    'DjangoHUDApp/credentials/google_credentials.json', scope
                )
                client = gspread.authorize(creds)
                sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xJGQFFkucEbFjJf8Y05x8OOcFp2e_ZxTz_rtjq7QQ1g/edit?gid=914811941#gid=914811941")
                worksheet = sheet.get_worksheet(0)

                # Append data to Google Sheets
                worksheet.append_row([ 
                    cleaned_data['org_name'],
                    cleaned_data['spoc_name'],
                    cleaned_data['designation'],
                    cleaned_data['phone_no'],
                    cleaned_data['email'],
                    cleaned_data['address'],
                    cleaned_data['location'],
                    cleaned_data['website'],
                    cleaned_data['source_data'],
                    cleaned_data['status'],
                    cleaned_data['feedback'],
                    cleaned_data['remark'],
                    cleaned_data['reference'],
                    cleaned_data['callback_date'],
                    cleaned_data['initiated_date'],
                    cleaned_data['followup_date'],
                ])

                # After successful save, redirect to the same page with success message
                return redirect('DjangoHUDApp:organization-data-list')  # Replace with your correct URL pattern

            except Exception as e:
                logger.error('Error storing data: %s', str(e))
                return JsonResponse({'success': False, 'message': 'Error saving data'}, status=500)

        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    else:  # Handle GET request to retrieve data from Google Sheets
        form = OrganizationDataForm()
        spreadsheet_data = get_spreadsheet_data()  # Fetch only from Google Sheets
        
        # Pass data to context for rendering in the template
        context = {
            'form': form,
            'data': spreadsheet_data,  # Spreadsheet data is used directly
            'success_message': request.GET.get('success_message', '')
        }
        return render(request, 'pages/organization-data-list.html', context)
    
def placement_training_view(request):
    if request.method == "POST":
        form = PlacementTrainingForm(request.POST)
        if form.is_valid():
            org_data = form.save(commit=False)
            status = form.cleaned_data.get('status')

            # Set the date fields based on user input, if provided
            if status == 'callback':
                org_data.callback_date = form.cleaned_data.get('callback_date')
            elif status == 'initiated':
                org_data.initiated_date = form.cleaned_data.get('initiated_date')
            elif status == 'follow up':
                org_data.followup_date = form.cleaned_data.get('followup_date')

            # Save the organization data
            org_data.save()

            # Convert datetime fields to strings for Google Sheets
            def convert_datetime_to_str(date_obj):
                return date_obj.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date_obj, datetime) else ''

            callback_date = convert_datetime_to_str(org_data.callback_date)
            initiated_date = convert_datetime_to_str(org_data.initiated_date)
            followup_date = convert_datetime_to_str(org_data.followup_date)

            try:
                # Google Sheets API setup and authorization
                scope = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    'DjangoHUDApp/credentials/google_credentials.json', scope
                )
                client = gspread.authorize(creds)
                sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xJGQFFkucEbFjJf8Y05x8OOcFp2e_ZxTz_rtjq7QQ1g/edit?gid=2049597071#gid=2049597071")
                worksheet = sheet.get_worksheet(1)

                # Append data to Google Sheets
                worksheet.append_row([
                    form.cleaned_data.get('org_name', ''),
                    form.cleaned_data.get('spoc_name', ''),
                    form.cleaned_data.get('designation', ''),
                    form.cleaned_data.get('phone_no', ''),
                    form.cleaned_data.get('email', ''),
                    form.cleaned_data.get('address', ''),
                    form.cleaned_data.get('location', ''),
                    form.cleaned_data.get('website', ''),
                    form.cleaned_data.get('source_data', ''),
                    form.cleaned_data.get('status', ''),
                    form.cleaned_data.get('feedback', ''),
                    form.cleaned_data.get('remark', ''),
                    form.cleaned_data.get('reference', ''),
                    callback_date,
                    initiated_date,
                    followup_date,
                ])

            except Exception as e:
                logger.error('Error updating Google Sheets: %s', str(e))
                return JsonResponse({'success': False, 'message': 'Google Sheets API error'}, status=503)

            # Redirect to the list view after saving
            return redirect('DjangoHUDApp:placement_training')
    else:
        form = PlacementTrainingForm()

    # Fetch existing data to display in the template
    data = PlacementTraining.objects.all()
    return render(request, 'pages/placement_training.html', {'form': form, 'data': data})

def training_data_view(request):
    # Google Sheets and Drive API scopes
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Helper function to convert date/datetime/time to string
    def convert_to_str(value):
        """Convert date, datetime, or time objects to string format."""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')  # Custom format for datetime
        elif isinstance(value, date):
            return value.strftime('%Y-%m-%d')  # Custom format for date
        elif isinstance(value, time):
            return value.strftime('%H:%M:%S')  # Custom format for time
        return str(value)  # Ensure other types are converted to string if necessary

    if request.method == 'POST':
        form = TrainingDataForm(request.POST)
        if form.is_valid():
            try:
                # Save form data to model
                training_data = form.save(commit=False)
                training_data.save()

                # Convert date/time fields to strings
                cleaned_data = form.cleaned_data
                for field in ['start_date', 'end_date']:  # Adjust field names as needed
                    if field in cleaned_data and cleaned_data[field]:
                        cleaned_data[field] = convert_to_str(cleaned_data[field])

                # Google Sheets API authorization and writing data
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    'DjangoHUDApp/credentials/google_credentials.json', scope
                )
                client = gspread.authorize(creds)
                sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xJGQFFkucEbFjJf8Y05x8OOcFp2e_ZxTz_rtjq7QQ1g/edit?gid=1990701816#gid=1990701816")
                worksheet = sheet.get_worksheet(2)  # Adjust worksheet index if needed

                # Prepare data for appending to Google Sheets
                data_to_append = [
                    convert_to_str(cleaned_data.get('training_name', '')),
                    convert_to_str(cleaned_data.get('trainer_name', '')),
                    convert_to_str(cleaned_data.get('date', '')),
                    convert_to_str(cleaned_data.get('duration', '')),
                    convert_to_str(cleaned_data.get('location', '')),
                    convert_to_str(cleaned_data.get('feedback', '')),
                    convert_to_str(cleaned_data.get('remarks', '')),
                    convert_to_str(cleaned_data.get('reference', ''))
                ]

                # Append data to Google Sheets
                worksheet.append_row(data_to_append)

                return redirect('DjangoHUDApp:training_data')

            except gspread.exceptions.APIError as api_error:
                logger.error('Google Sheets API error: %s', api_error)
                return JsonResponse({'success': False, 'message': f'Google Sheets API error: {str(api_error)}'}, status=503)

            except Exception as e:
                logger.error('Error saving data: %s', str(e))
                return JsonResponse({'success': False, 'message': f'Error saving data: {str(e)}'}, status=503)

        else:
            # Log form errors if form validation fails
            logger.error("Form validation failed: %s", form.errors)
            return JsonResponse({'success': False, 'message': 'Invalid form data', 'errors': form.errors}, status=400)

    else:
        form = TrainingDataForm()

    # Fetch existing training data to display
    data = TrainingData.objects.all()
    return render(request, 'pages/training_data.html', {'form': form, 'data': data})

def corporate_training_view(request):
    # Google Sheets and Drive API scopes
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Helper function to convert date/datetime/time to string
    def convert_to_str(value):
        """Convert date, datetime, or time objects to string format."""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')  # Custom format for datetime
        elif isinstance(value, date):
            return value.strftime('%Y-%m-%d')  # Custom format for date
        elif isinstance(value, time):
            return value.strftime('%H:%M:%S')  # Custom format for time
        return str(value)  # Ensure other types are converted to string if necessary

    if request.method == 'POST':
        form = CorporateTrainingForm(request.POST)
        if form.is_valid():
            try:
                # Save form data to model
                corporate_training = form.save(commit=False)
                corporate_training.save()

                # Convert date/time fields to strings (if applicable)
                cleaned_data = form.cleaned_data
                for field in ['training_date']:  # Adjust field names if necessary
                    if field in cleaned_data and cleaned_data[field]:
                        cleaned_data[field] = convert_to_str(cleaned_data[field])

                # Google Sheets API authorization and writing data
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    'DjangoHUDApp/credentials/google_credentials.json', scope
                )
                client = gspread.authorize(creds)
                sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xJGQFFkucEbFjJf8Y05x8OOcFp2e_ZxTz_rtjq7QQ1g/edit?gid=1860153422#gid=1860153422")
                worksheet = sheet.get_worksheet(3)  # Adjust worksheet index if needed

                # Prepare data for appending to Google Sheets
                data_to_append = [
                    convert_to_str(cleaned_data.get('course_name', '')),
                    convert_to_str(cleaned_data.get('trainer_name', '')),
                    convert_to_str(cleaned_data.get('date', '')),
                    convert_to_str(cleaned_data.get('duration', '')),
                    convert_to_str(cleaned_data.get('location', '')),
                    convert_to_str(cleaned_data.get('participants_count', '')),
                    convert_to_str(cleaned_data.get('cost', '')),
                    convert_to_str(cleaned_data.get('feedback', ''))
                ]

                # Append data to Google Sheets
                worksheet.append_row(data_to_append)

                return redirect('DjangoHUDApp:corporate_training')

            except gspread.exceptions.APIError as api_error:
                logger.error('Google Sheets API error: %s', api_error)
                return JsonResponse({'success': False, 'message': f'Google Sheets API error: {str(api_error)}'}, status=503)

            except Exception as e:
                logger.error('Error saving data: %s', str(e))
                return JsonResponse({'success': False, 'message': f'Error saving data: {str(e)}'}, status=503)

        else:
            # Log form errors if form validation fails
            logger.error("Form validation failed: %s", form.errors)
            return JsonResponse({'success': False, 'message': 'Invalid form data', 'errors': form.errors}, status=400)

    else:
        form = CorporateTrainingForm()

    # Fetch existing corporate training data to display
    data = CorporateTraining.objects.all()  # Adjust based on your model
    return render(request, 'pages/corporate-training.html', {'form': form, 'data': data})

def pageadmin(request):
    context = {
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0'
    }
    return render(request, "pages/page-admin.html", context)


def index(request):
    return render(request, "pages/index.html") 






@csrf_exempt
def profileadd(request):
    print(f"Request method: {request.method}")
    if request.method == 'GET':
        # Render the form template on a GET request
        print("Rendering GET form")
        context = {
            "appSidebarHide": 1,
            "appHeaderHide": 1,
            "appContentClass": 'p-0',
            "profile": None,  # You may replace `None` with an actual profile object if needed
        }
        return render(request, 'pages/profile-add.html', context)

    elif request.method == 'POST':
        try:
            # Extract form data from request
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            gender = request.POST.get('gender')
            birth_date = request.POST.get('birth_date')
            mobile_number = request.POST.get('mobile_number')
            email = request.POST.get('email')
            college_name = request.POST.get('college_name')
            id_number = request.POST.get('id_number')
            batch_number = request.POST.get('batch_number')
            city = request.POST.get('city')
            address = request.POST.get('address')
            state = request.POST.get('state')
            country = request.POST.get('country')
            qualification = request.POST.get('qualification')
            role = request.POST.get('role')
            language = request.POST.get('language')
            skills = request.POST.get('skills')
            locations = request.POST.get('locations')
            bank_name = request.POST.get('bank_name')
            branch_name = request.POST.get('branch_name')
            ifsc_code = request.POST.get('ifsc_code')
            account_number = request.POST.get('account_number')
            pan_number = request.POST.get('pan_number')
            gst_number = request.POST.get('gst_number')
            photo = request.POST.get('photo')
            certificate = request.POST.get('certificate')
            ready_to_relocate = request.POST.get('ready_to_relocate')
            resume = request.POST.get('resume')
            experience = request.POST.get('experience')

            # Path to your service account credentials
            SERVICE_ACCOUNT_FILE = 'E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
           
            # The ID of the Google Spreadsheet and range
            SPREADSHEET_ID = '1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE'
            RANGE_NAME = 'profile!A:Z'

            # Define the scope
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # Load the credentials
            credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

            # Build the Google Sheets API service
            service = build('sheets', 'v4', credentials=credentials)

            # Data to append
            data = [[
                name, email, password, gender, birth_date, mobile_number, college_name,
                id_number, batch_number, city, address, state, country, qualification, role,
                language, skills, locations, bank_name, branch_name, ifsc_code,
                account_number, pan_number, gst_number, photo, certificate, resume, ready_to_relocate, experience
            ]]
            body = {'values': data}

            # Append data to the spreadsheet
            sheet = service.spreadsheets()
            result = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption='RAW',
                body=body
            ).execute()
            return redirect("DjangoHUDApp:pageLogin")

        except Exception as e:
            # Handle errors and send a 500 error if needed
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Handle invalid request method
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request method. Only GET and POST are allowed.'}, status=405)





def profileupdate(request):
    profile = None

    # Handle search by email
    if 'search_email' in request.GET:
        search_email = request.GET['search_email']
        try:
            profile = Profile.objects.get(email=search_email)
        except Profile.DoesNotExist:
            messages.error(request, 'No profile found for the given email.')
            profile = None

    # Handle form submission for update or delete
    if request.method == 'POST' and profile:
        if 'update' in request.POST:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('DjangoHUDApp:landing')  # Redirect after successful update
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'delete' in request.POST:
            profile.delete()
            messages.success(request, 'Profile deleted successfully.')
            return redirect('DjangoHUDApp:profileupdate')  # Redirect after deletion

    # Pass the profile to the template for display
    context = {
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0',
        "profile": profile,
    }
    return render(request, 'pages/profile-update.html', context)







# def profiledelete(request):
#     context = {
#         "appSidebarHide": 1,
#         "appHeaderHide": 1,
#         "appContentClass": 'p-0'
#     }
#     return render(request, "pages/profile-delete.html", context)








def analytics(request):
	return render(request, "pages/analytics.html")

def emailInbox(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-3"
	}
	return render(request, "pages/email-inbox.html", context)

def emailDetail(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-3"
	}
	return render(request, "pages/email-detail.html", context)

def emailCompose(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-3"
	}
	return render(request, "pages/email-compose.html", context)

def widgets(request):
	return render(request, "pages/widgets.html")

def posCustomerOrder(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-customer-order.html", context)

def posKitchenOrder(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-kitchen-order.html", context)

def posCounterCheckout(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-counter-checkout.html", context)

def posTableBooking(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-table-booking.html", context)

def posMenuStock(request):
	context = {
		"appSidebarHide": 1, 
		"appHeaderHide": 1,  
		"appContentFullHeight": 1,
		"appContentClass": "p-1 ps-xl-4 pe-xl-4 pt-xl-3 pb-xl-3"
	}
	return render(request, "pages/pos-menu-stock.html", context)

def uiBootstrap(request):
	return render(request, "pages/ui-bootstrap.html")

def uiButtons(request):
	return render(request, "pages/ui-buttons.html")

def uiCard(request):
	return render(request, "pages/ui-card.html")

def uiIcons(request):
	return render(request, "pages/ui-icons.html")

def uiModalNotifications(request):
	return render(request, "pages/ui-modal-notifications.html")

def uiTypography(request):
	return render(request, "pages/ui-typography.html")

def uiTabsAccordions(request):
	return render(request, "pages/ui-tabs-accordions.html")

def formElements(request):
	return render(request, "pages/form-elements.html")

def formPlugins(request):
	return render(request, "pages/form-plugins.html")

def formWizards(request):
	return render(request, "pages/form-wizards.html")

def tableElements(request):
	return render(request, "pages/table-elements.html")

def tablePlugins(request):
	return render(request, "pages/table-plugins.html")

def chartJs(request):
	return render(request, "pages/chart-js.html")

def chartApex(request):
	return render(request, "pages/chart-apex.html")

def map(request):
	return render(request, "pages/map.html")

def layoutStarter(request):
	return render(request, "pages/layout-starter.html")

def layoutFixedFooter(request):
	context = {
		"appFooter": 1
	}
	return render(request, "pages/layout-fixed-footer.html", context)

def layoutFullHeight(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-0"
	}
	return render(request, "pages/layout-full-height.html", context)

def layoutFullWidth(request):
	context = {
		"appContentFullWidth": 1,
		"appSidebarHide": 1
	}
	return render(request, "pages/layout-full-width.html", context)

def layoutBoxedLayout(request):
	context = {
		"appBoxedLayout": 1,
		"bodyClass": "pace-top"
	}
	return render(request, "pages/layout-boxed-layout.html", context)

def layoutCollapsedSidebar(request):
	context = {
		"appSidebarCollapsed": 1
	}
	return render(request, "pages/layout-collapsed-sidebar.html", context)

def layoutTopNav(request):
	context = {
		"appTopNav": 1,
		"appSidebarHide": 1
	}
	return render(request, "pages/layout-top-nav.html", context)

def layoutMixedNav(request):
	context = {
		"appTopNav": 1,
	}
	return render(request, "pages/layout-mixed-nav.html", context)

def layoutMixedNavBoxedLayout(request):
	context = {
		"appTopNav": 1,
		"appBoxedLayout": 1
	}
	return render(request, "pages/layout-mixed-nav-boxed-layout.html", context)

def pageScrumBoard(request):
	return render(request, "pages/page-scrum-board.html")

def pageProduct(request):
	return render(request, "pages/page-product.html")

def pageProductDetails(request):
	return render(request, "pages/page-product-details.html")

def pageOrder(request):
	return render(request, "pages/page-order.html")

def pageOrderDetails(request):
	return render(request, "pages/page-order-details.html")

def pageGallery(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'p-0',
		"appSidebarCollapsed": 1
	}
	return render(request, "pages/page-gallery.html", context)

def pageSearchResults(request):
	return render(request, "pages/page-search-results.html")

def pageComingSoon(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-coming-soon.html", context)

def pageError(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-error.html", context)


def pageMessenger(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'p-3'
	}
	return render(request, "pages/page-messenger.html", context)

def pageDataManagement(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'py-3'
	}
	return render(request, "pages/page-data-management.html", context)

def pageFileManager(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": 'd-flex flex-column'
	}
	return render(request, "pages/page-file-manager.html", context)

def pagePricing(request):
	return render(request, "pages/page-pricing.html")



def profile(request):
	return render(request, "pages/profile.html")

def calendar(request):
	context = {
		"appContentFullHeight": 1,
		"appContentClass": "p-0"
	}
	return render(request, "pages/calendar.html", context)

def settings(request):
	return render(request, "pages/settings.html")

def helper(request):
	return render(request, "pages/helper.html")
	
def error404(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/page-error.html", context)

def handler404(request, exception = None):
	return redirect('/404/')