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
from django.core.files.storage import FileSystemStorage
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from django.core.cache import cache







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
    RANGE_NAME = 'profile!A:AE'

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
                if email.strip() == row[1].strip() and password.strip() == row[2].strip() and row[29].strip() == "0":
                    role = row[14].strip()
                    delete=row[29].strip()
                    print(f"Retrieved role for {email}: {role}")
                    print(f"Retrieved role for {email}: {delete}")  # Debug: Print the role
                      # Debug: Print the role

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
                        range_name='login!A:AK',
                        service_account_file='E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
                    )
                     # Redirect based on role
                    if role.strip().lower() == 'admin':
                        print(f"Redirecting {email} to organization-data-list")  
                        return redirect('DjangoHUDApp:organization-data-list')
                    elif role.strip().lower() == 'manager':
                        print(f"redirecting {email} to placement_training")
                        return redirect('DjangoHUDApp:placement_training')
                   
                    elif role.strip().lower() == 'trainer':
                        print(f"redirecting {email} to corporate_training")
                        return redirect('DjangoHUDApp:corporate_training')
                    else:
                        print(f"Redirecting {email} to landing")  
                        return redirect('DjangoHUDApp:landing')

            return JsonResponse({'error': 'Invalid credentialsss.'}, status=401)
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






from django.http import HttpResponseForbidden
from functools import wraps

    
logger = logging.getLogger(__name__)

#----==================== Role Based Access ===================------------------

def admin_or_superadmin_required(view_func):
    """Decorator to restrict access to admins or superadmins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is logged in and has the required role
        email = request.session.get('email')
        role = None
        if email:
            # Fetch data from Google Sheet to validate the user's role
            sheet_data = get_sheet_data()
            for row in sheet_data[1:]:  # Skip header row
                if email.strip() == row[1].strip():  # Match email
                    role = row[14].strip()  # Assuming role is at column 14
                    break
        
        if role and role.lower() in ['admin', 'superadmin']:
            return view_func(request, *args, **kwargs)
        else:
            # Deny access for non-admins or non-superadmins
            return HttpResponseForbidden("You do not have permission to access this page.")
    
    return wrapper

def manager_or_superadmin_required(view_func):
    """Decorator to restrict access to admins or superadmins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is logged in and has the required role
        email = request.session.get('email')
        role = None
        if email:
            # Fetch data from Google Sheet to validate the user's role
            sheet_data = get_sheet_data()
            for row in sheet_data[1:]:  # Skip header row
                if email.strip() == row[1].strip():  # Match email
                    role = row[14].strip()  # Assuming role is at column 14
                    break
        
        if role and role.lower() in ['manager', 'superadmin']:
            return view_func(request, *args, **kwargs)
        else:
            # Deny access for non-admins or non-superadmins
            return HttpResponseForbidden("You do not have permission to access this page.")
    
    return wrapper


def user_or_superadmin_required(view_func):
    """Decorator to restrict access to admins or superadmins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is logged in and has the required role
        email = request.session.get('email')
        role = None
        if email:
            # Fetch data from Google Sheet to validate the user's role
            sheet_data = get_sheet_data()
            for row in sheet_data[1:]:  # Skip header row
                if email.strip() == row[1].strip():  # Match email
                    role = row[14].strip()  # Assuming role is at column 14
                    break
        
        if role and role.lower() in ['user', 'superadmin']:
            return view_func(request, *args, **kwargs)
        else:
            # Deny access for non-admins or non-superadmins
            return HttpResponseForbidden("You do not have permission to access this page.")
    
    return wrapper


def trainer_or_superadmin_required(view_func):
    """Decorator to restrict access to admins or superadmins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is logged in and has the required role
        email = request.session.get('email')
        role = None
        if email:
            # Fetch data from Google Sheet to validate the user's role
            sheet_data = get_sheet_data()
            for row in sheet_data[1:]:  # Skip header row
                if email.strip() == row[1].strip():  # Match email
                    role = row[14].strip()  # Assuming role is at column 14
                    break
        
        if role and role.lower() in ['trainer', 'superadmin']:
            return view_func(request, *args, **kwargs)
        else:
            # Deny access for non-admins or non-superadmins
            return HttpResponseForbidden("You do not have permission to access this page.")
    
    return wrapper

#--------========================================================-------------------


#=================== organization-data-list =================================
# Google Sheets authorization scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@csrf_protect
@admin_or_superadmin_required
def organization_data_list(request):
    """
    Handles Google Sheets integration, including form submissions, auto-save requests,
    and rendering data for placement training.
    """

    def get_google_sheets_client():
        """Returns the Google Sheets client."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'DjangoHUDApp/credentials/google_credentials.json',
                [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE/edit?gid=2024647455#gid=2024647455"
            )
            return sheet.get_worksheet(0)
        except Exception as e:
            logger.error("Error obtaining Google Sheets client: %s", e)
            raise

    def convert_datetime_to_str(date_obj):
        """Converts datetime or date object to string."""
        if isinstance(date_obj, (datetime.datetime, datetime.date)):
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        elif date_obj is None:
            return 'No Date'
        else:
            raise ValueError(f"Unsupported type for date_obj: {type(date_obj)}")

    def get_spreadsheet_data_from_sheets():
        """Fetches data from Google Sheets directly."""
        try:
            worksheet = make_request_with_retries(get_google_sheets_client)
            rows = worksheet.get_all_values()
            if rows:
                header = rows[0]
                data = [
                    dict(zip(header, row))
                    for row in rows[1:]
                    if row[16].strip() != '1'  # Exclude rows marked as deleted
                ]
                return data
            return []
        except Exception as e:
            logger.error("Error retrieving Google Sheets data: %s", e)
            return []

    def get_spreadsheet_data():
        """Fetches data from cache or Google Sheets."""
        cached_data = cache.get('spreadsheet_data')
        if cached_data:
            return cached_data

        data = get_spreadsheet_data_from_sheets()  # Fetch from Sheets
        cache.set('spreadsheet_data', data, timeout=60 * 10)  # Cache for 5 minutes
        return data

    def make_request_with_retries(request_func, retries=10, delay=1):
        """Retry API requests with exponential backoff."""
        for i in range(retries):
            try:
                return request_func()
            except HttpError as err:
                if err.resp.status == 429:  # Rate limit exceeded
                    wait_time = delay * (2 ** i)  # Exponential backoff
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception("Max retries reached, request failed.")

    def handle_ajax_requests(request):
        """Handles AJAX requests for auto-save and delete actions."""
        try:
            row_data = json.loads(request.body)
            action = row_data.get('action')

            worksheet = make_request_with_retries(get_google_sheets_client)
            records = worksheet.get_all_values()

            if action == 'delete':
                record_id = row_data.get('id')
                row_index = next(
                    (index for index, row in enumerate(records, start=1) if row[17] == record_id), None
                )
                if row_index:
                    worksheet.update_cell(row_index, 17, "1")  # Mark as deleted
                    return JsonResponse({'success': True, 'message': 'Row marked as deleted.'})
                return JsonResponse({'success': False, 'message': 'Record ID not found.'}, status=404)

            elif action == 'autosave':
                record_id = row_data.get('id')
                col_index = int(row_data.get('col_index')) + 1
                value = row_data.get('value')

                row_index = next(
                    (index for index, row in enumerate(records, start=1) if row[17] == record_id), None
                )
                if row_index:
                    worksheet.update_cell(row_index, col_index, value)
                    submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.update_cell(row_index, 21, request.session.get('email', 'Unknown'))
                    worksheet.update_cell(row_index, 22, submission_time)
                    return JsonResponse({'success': True, 'message': 'Auto-saved successfully.'})
                return JsonResponse({'success': False, 'message': 'Record ID not found.'}, status=404)

        except Exception as e:
            logger.error("Error processing AJAX request: %s", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def handle_form_submission(request):
        """Handles form submissions."""
        form = OrganizationDataForm(request.POST)
        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                for field in ['callback_date', 'initiated_date', 'followup_date']:
                    cleaned_data[field] = convert_datetime_to_str(cleaned_data.get(field))
                cleaned_data['deleted'] = '0'
                submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                worksheet = make_request_with_retries(get_google_sheets_client)
                current_row_count = len(worksheet.get_all_values()) - 1
                next_id = current_row_count + 1

                worksheet.append_row([ 
                    cleaned_data['org_name'], cleaned_data['spoc_name'], cleaned_data['designation'],
                    cleaned_data['phone_no'], cleaned_data['email'], cleaned_data['address'],
                    cleaned_data['location'], cleaned_data['website'], cleaned_data['source_data'],
                    cleaned_data['status'], cleaned_data['feedback'], cleaned_data['remark'],
                    cleaned_data['reference'], cleaned_data['callback_date'], cleaned_data['initiated_date'],
                    cleaned_data['followup_date'], cleaned_data['deleted'], next_id,
                    request.session.get('email', 'Unknown'), submission_time
                ])
                # Clear cache after form submission to ensure updated data is fetched next time
                cache.delete('spreadsheet_data')
                return redirect('DjangoHUDApp:organization-data-list')
            except Exception as e:
                logger.error("Error storing data: %s", str(e))
                return JsonResponse({'success': False, 'message': 'Error saving data'}, status=500)

        logger.error("Form errors: %s", form.errors)
        return JsonResponse({'success': False, 'message': 'Invalid form submission', 'errors': form.errors}, status=400)

    # Main logic for the view
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_requests(request)
        return handle_form_submission(request)

    try:
        data = get_spreadsheet_data()
    except Exception as e:
        logger.error("Error fetching spreadsheet data: %s", e)
        data = []

    return render(request, 'pages/organization-data-list.html', {'form': OrganizationDataForm(), 'data': data})

#============================================================


#===================== placement_training_view =================================

@csrf_protect
@manager_or_superadmin_required
def placement_training_view(request):
    """
    Handles Google Sheets integration, including form submissions, auto-save requests,
    and rendering data for placement training.
    """

    def get_google_sheets_client():
        """Returns the Google Sheets client."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'DjangoHUDApp/credentials/google_credentials.json',
                [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE/edit#gid=1150146711"
            )
            return sheet.get_worksheet(1)
        except Exception as e:
            logger.error("Error obtaining Google Sheets client: %s", e)
            raise

    def convert_datetime_to_str(date_obj):
        """Converts datetime or date object to string."""
        if isinstance(date_obj, (datetime.datetime, datetime.date)):
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        elif date_obj is None:
            return 'No Date'
        else:
            raise ValueError(f"Unsupported type for date_obj: {type(date_obj)}")

    def get_spreadsheet_data_from_sheets():
        """Fetches data from Google Sheets directly."""
        try:
            worksheet = make_request_with_retries(get_google_sheets_client)
            rows = worksheet.get_all_values()
            if rows:
                header = rows[0]
                data = [
                    dict(zip(header, row))
                    for row in rows[1:]
                    if row[16].strip() != '1'  # Exclude rows marked as deleted
                ]
                return data
            return []
        except Exception as e:
            logger.error("Error retrieving Google Sheets data: %s", e)
            return []

    def get_spreadsheet_data():
        """Fetches data from cache or Google Sheets."""
        cached_data = cache.get('spreadsheet_data')
        if cached_data:
            return cached_data

        data = get_spreadsheet_data_from_sheets()  # Fetch from Sheets
        cache.set('spreadsheet_data', data, timeout=60 * 5)  # Cache for 5 minutes
        return data

    def make_request_with_retries(request_func, retries=5, delay=1):
        """Retry API requests with exponential backoff."""
        for i in range(retries):
            try:
                return request_func()
            except HttpError as err:
                if err.resp.status == 429:  # Rate limit exceeded
                    wait_time = delay * (2 ** i)  # Exponential backoff
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception("Max retries reached, request failed.")

    def handle_ajax_requests(request):
        """Handles AJAX requests for auto-save and delete actions."""
        try:
            row_data = json.loads(request.body)
            action = row_data.get('action')

            worksheet = make_request_with_retries(get_google_sheets_client)
            records = worksheet.get_all_values()

            if action == 'delete':
                record_id = row_data.get('id')
                row_index = next(
                    (index for index, row in enumerate(records, start=1) if row[17] == record_id), None
                )
                if row_index:
                    worksheet.update_cell(row_index, 17, "1")  # Mark as deleted
                    return JsonResponse({'success': True, 'message': 'Row marked as deleted.'})
                return JsonResponse({'success': False, 'message': 'Record ID not found.'}, status=404)

            elif action == 'autosave':
                record_id = row_data.get('id')
                col_index = int(row_data.get('col_index')) + 1
                value = row_data.get('value')

                row_index = next(
                    (index for index, row in enumerate(records, start=1) if row[17] == record_id), None
                )
                if row_index:
                    worksheet.update_cell(row_index, col_index, value)
                    submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.update_cell(row_index, 21, request.session.get('email', 'Unknown'))
                    worksheet.update_cell(row_index, 22, submission_time)
                    return JsonResponse({'success': True, 'message': 'Auto-saved successfully.'})
                return JsonResponse({'success': False, 'message': 'Record ID not found.'}, status=404)

        except Exception as e:
            logger.error("Error processing AJAX request: %s", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def handle_form_submission(request):
        """Handles form submissions."""
        form = PlacementTrainingForm(request.POST)
        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                for field in ['callback_date', 'initiated_date', 'followup_date']:
                    cleaned_data[field] = convert_datetime_to_str(cleaned_data.get(field))
                cleaned_data['deleted'] = '0'
                submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                worksheet = make_request_with_retries(get_google_sheets_client)
                current_row_count = len(worksheet.get_all_values()) - 1
                next_id = current_row_count + 1

                worksheet.append_row([ 
                    cleaned_data['org_name'], cleaned_data['spoc_name'], cleaned_data['designation'],
                    cleaned_data['phone_no'], cleaned_data['email'], cleaned_data['address'],
                    cleaned_data['location'], cleaned_data['website'], cleaned_data['source_data'],
                    cleaned_data['status'], cleaned_data['feedback'], cleaned_data['remark'],
                    cleaned_data['reference'], cleaned_data['callback_date'], cleaned_data['initiated_date'],
                    cleaned_data['followup_date'], cleaned_data['deleted'], next_id,
                    request.session.get('email', 'Unknown'), submission_time
                ])
                # Clear cache after form submission to ensure updated data is fetched next time
                cache.delete('spreadsheet_data')
                return redirect('DjangoHUDApp:placement_training')
            except Exception as e:
                logger.error("Error storing data: %s", str(e))
                return JsonResponse({'success': False, 'message': 'Error saving data'}, status=500)

        logger.error("Form errors: %s", form.errors)
        return JsonResponse({'success': False, 'message': 'Invalid form submission', 'errors': form.errors}, status=400)

    # Main logic for the view
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_requests(request)
        return handle_form_submission(request)

    try:
        data = get_spreadsheet_data()
    except Exception as e:
        logger.error("Error fetching spreadsheet data: %s", e)
        data = []

    return render(request, 'pages/placement_training.html', {'form': PlacementTrainingForm(), 'data': data})

#===============================================================================

#================= training_data_view ==========================================
# Google Sheets authorization scope

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@csrf_protect
@user_or_superadmin_required
def training_data_view(request):
    """
    Handles Google Sheets integration, including form submissions, auto-save requests,
    and rendering data for placement training.
    """

    def get_google_sheets_client():
        """Returns the Google Sheets client."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'DjangoHUDApp/credentials/google_credentials.json',
                [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE/edit?gid=1607700667#gid=1607700667"
            )
            return sheet.get_worksheet(2)
        except Exception as e:
            logger.error("Error obtaining Google Sheets client: %s", e)
            raise

    def convert_datetime_to_str(date_obj):
        """Converts datetime or date object to string."""
        if isinstance(date_obj, (datetime.datetime, datetime.date)):
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        elif date_obj is None:
            return 'No Date'
        else:
            raise ValueError(f"Unsupported type for date_obj: {type(date_obj)}")

    def get_spreadsheet_data_from_sheets():
        try:
            worksheet = make_request_with_retries(get_google_sheets_client)
            rows = worksheet.get_all_values()
            logger.info(f"Rows retrieved from Google Sheet: {rows}")  # Add this
            if rows:
                header = rows[0]
                data = [
                    dict(zip(header, row))
                    for row in rows[1:]
                    if len(row) >= 10 and row[10].strip() != '1'  # Exclude rows marked as deleted
                ]
                logger.info(f"Processed data: {data}")  # Add this
                return data
            return []
        except Exception as e:
            logger.error("Error retrieving Google Sheets data: %s", e)
            return []

    def get_spreadsheet_data(bypass_cache=False):
        if not bypass_cache:
            cached_data = cache.get('spreadsheet_data')
            logger.info(f"Cached data: {cached_data}")  # Add this
            if cached_data:
                return cached_data

        data = get_spreadsheet_data_from_sheets()
        cache.set('spreadsheet_data', data, timeout=60 * 10)
        return data

    def make_request_with_retries(request_func, retries=10, delay=1):
        """Retry API requests with exponential backoff."""
        for i in range(retries):
            try:
                return request_func()
            except HttpError as err:
                if err.resp.status == 429:  # Rate limit exceeded
                    wait_time = delay * (2 ** i)  # Exponential backoff
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception("Max retries reached, request failed.")

    def handle_ajax_requests(request):
        """Handles AJAX requests for auto-save and delete actions."""
        try:
            row_data = json.loads(request.body)
            action = row_data.get('action')

            worksheet = make_request_with_retries(get_google_sheets_client)
            records = worksheet.get_all_values()

            if action == 'delete':
                record_id = row_data.get('id')
                row_index = next(
                    (index for index, row in enumerate(records, start=1) if row[11] == record_id), None
                )
                if row_index:
                    worksheet.update_cell(row_index, 10, "1")  # Mark as deleted
                    return JsonResponse({'success': True, 'message': 'Row marked as deleted.'})
                return JsonResponse({'success': False, 'message': 'Record ID not found.'}, status=404)

            elif action == 'autosave':
                record_id = row_data.get('id')
                col_index = int(row_data.get('col_index')) + 1
                value = row_data.get('value')

                row_index = next(
                    (index for index, row in enumerate(records, start=1) if row[11] == record_id), None
                )
                if row_index:
                    worksheet.update_cell(row_index, col_index, value)
                    submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.update_cell(row_index, 14, request.session.get('email', 'Unknown'))
                    worksheet.update_cell(row_index, 15, submission_time)
                    return JsonResponse({'success': True, 'message': 'Auto-saved successfully.'})
                return JsonResponse({'success': False, 'message': 'Record ID not found.'}, status=404)

        except Exception as e:
            logger.error("Error processing AJAX request: %s", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def handle_form_submission(request):
        form = TrainingDataForm(request.POST)
        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                cleaned_data['deleted'] = '0'
                submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                worksheet = make_request_with_retries(get_google_sheets_client)
                current_row_count = len(worksheet.get_all_values()) - 1
                next_id = current_row_count + 1

                worksheet.append_row([
                    cleaned_data['training_name'],
                    cleaned_data['trainer_name'],
                    str(cleaned_data['date']),
                    str(cleaned_data['duration']),
                    cleaned_data['location'],
                    cleaned_data['feedback'],
                    cleaned_data['remarks'],
                    cleaned_data['reference'],
                    cleaned_data['deleted'],
                    next_id,
                    request.session.get('email', 'Unknown'),
                    submission_time,
                ])
                # Fetch updated data bypassing cache
                data_to_display = get_spreadsheet_data(bypass_cache=True)  
                return render(request, 'pages/training_data.html', {'form': TrainingDataForm(), 'data': data_to_display})
            except Exception as e:
                logger.error("Error storing data: %s", str(e))
                return JsonResponse({'success': False, 'message': 'Error saving data'}, status=500)

        logger.error("Form errors: %s", form.errors)
        return JsonResponse({'success': False, 'message': 'Invalid form submission', 'errors': form.errors}, status=400)

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_requests(request)
        return handle_form_submission(request)

    try:
        data = get_spreadsheet_data()
    except Exception as e:
        logger.error("Error fetching spreadsheet data: %s", e)
        data = []

    # Filtering data to exclude rows where 'deleted' is '1'
    data_to_display = [entry for entry in data if entry.get('deleted', '0') == '0']

    return render(request, 'pages/training_data.html', {'form': TrainingDataForm(), 'data': data_to_display})

#===============================================================================
from decimal import Decimal

#==================== corporate_training_view ==================================
@trainer_or_superadmin_required
def corporate_training_view(request):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def convert_to_str(value):
        """Convert various data types to string format."""
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, datetime.time):
            return value.strftime('%H:%M:%S')
        elif isinstance(value, Decimal):
            return str(value)  # Convert Decimal to string for JSON compatibility
        return str(value)

    def fetch_google_sheet_data():
        """Fetch all data from the Google Sheets worksheet."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'DjangoHUDApp/credentials/google_credentials.json', scope
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE/edit#gid=599886608"
            )
            worksheet = sheet.get_worksheet(3)  # Ensure correct worksheet index
            return worksheet.get_all_records()  # Fetch all records as a list of dictionaries
        except Exception as e:
            logger.error(f"Error fetching Google Sheets data: {str(e)}")
            return []  # Return an empty list if an error occurs
        
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Parse the data from the AJAX request
            row_data = json.loads(request.body)
            print(f"Received data: {row_data}")

            # Check if row_index and col_index are in the data
            row_index = int(row_data['row_index']) + 1  # Adjust for header row
            col_index = int(row_data['col_index']) + 1 # Adjust for 1-based indexing
            value = row_data['value']
            print(f"row_index: {row_index}, col_index: {col_index}")

            # Check if row_index and col_index are valid
            if row_index is None or col_index is None:
                return JsonResponse({'success': False, 'message': 'Row or column index missing!'}, status=400)
            print(f"row_index: {row_index}, col_index: {col_index}, value: {value}")

            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'DjangoHUDApp/credentials/google_credentials.json', scope
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE/edit?gid=599886608#gid=599886608"
            )
            worksheet = sheet.get_worksheet(3)

            # Update the specific row and column in the spreadsheet
            row_index = int(row_index) + 1  # Adjust for header row
            col_index = int(col_index) # Adjust for 1-based indexing
            worksheet.update_cell(row_index, col_index, row_data['value'])

            # Fetch updated data
            rows = worksheet.get_all_values()
            return JsonResponse({'success': True, 'message': 'Auto-saved successfully.', 'data': rows})

        except Exception as e:
            logger.error("Error in auto-save: %s", str(e))
            return JsonResponse({'success': False, 'message': 'Failed to auto-save data.'}, status=500)

    if request.method == 'POST':
        form = CorporateTrainingForm(request.POST)
        if form.is_valid():
            try:
                # Extract cleaned data
                cleaned_data = {key: convert_to_str(value) for key, value in form.cleaned_data.items()}

                # Google Sheets authorization
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    'DjangoHUDApp/credentials/google_credentials.json', scope
                )
                client = gspread.authorize(creds)
                sheet = client.open_by_url(
                    "https://docs.google.com/spreadsheets/d/1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE/edit#gid=599886608"
                )
                worksheet = sheet.get_worksheet(3)

                # Prepare data for appending
                data_to_append = [
                    cleaned_data.get('course_name', ''),
                    cleaned_data.get('trainer_name', ''),
                    cleaned_data.get('date', ''),  # Converted date field
                    cleaned_data.get('duration', ''),
                    cleaned_data.get('location', ''),
                    cleaned_data.get('participants_count', ''),
                    cleaned_data.get('cost', ''),
                    cleaned_data.get('feedback', '')
                ]

                # Append to Google Sheets
                worksheet.append_row(data_to_append)
                logger.info("Data successfully appended to Google Sheets.")
                return redirect('DjangoHUDApp:corporate_training')

            except Exception as e:
                logger.error(f"Error saving data: {str(e)}")
                return JsonResponse({'success': False, 'message': f'Error saving data: {str(e)}'}, status=500)

    else:
        form = CorporateTrainingForm()

    # Fetch live data from Google Sheets for template rendering
    data = fetch_google_sheet_data()

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
        return render(request, 'pages/profile-add.html')
    

    elif request.method == 'POST':
        try:
            # Extract form data from request
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            gender = request.POST.get('gender')
            birth_date = request.POST.get('birth_date')
            mobile_number = request.POST.get('mobile_number')
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
           
            ready_to_relocate = request.POST.get('ready_to_relocate')
            experience = request.POST.get('experience')
            # Handle file uploads
            photo = request.FILES.get('photo')
            certificate = request.FILES.get('certificate')
            resume = request.FILES.get('resume')


            # Define storage paths
            photo_storage = FileSystemStorage(location='media/photos/')
            certificate_storage = FileSystemStorage(location='media/certificates/')
            resume_storage = FileSystemStorage(location='media/resumes/')

            # Save files to respective folders
            photo_url = photo_storage.save(photo.name, photo) if photo else None
            certificate_url = certificate_storage.save(certificate.name, certificate) if certificate else None
            resume_url = resume_storage.save(resume.name, resume) if resume else None

            # Get accessible URLs
            photo_url = photo_storage.url(photo_url) if photo_url else None
            certificate_url = certificate_storage.url(certificate_url) if certificate_url else None
            resume_url = resume_storage.url(resume_url) if resume_url else None

            # Path to your service account credentials
            SERVICE_ACCOUNT_FILE = 'E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
           
            # The ID of the Google Spreadsheet and range
            SPREADSHEET_ID = '1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE'
            RANGE_NAME = 'profile!A:AH'

            # Define the scope
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # Load the credentials
            credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

            # Build the Google Sheets API service
            service = build('sheets', 'v4', credentials=credentials)
            # Retrieve current user and current datetime
            created_by = request.session.get('email', 'Anonymous')
            created_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Data to append
            data = [[
                name, email, password, gender, birth_date, mobile_number, college_name,
                id_number, batch_number, city, address, state, country, qualification, role,
                language, skills, locations, bank_name, branch_name, ifsc_code,
                account_number, pan_number, gst_number, photo_url, certificate_url, resume_url, ready_to_relocate, experience,"0",created_by, created_date
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
            success_message = "Your data has been successfully submitted."
            return render(request, 'pages/profile-add.html', {'success': success_message})

        except Exception as e:
            # Handle errors and send a 500 error if needed
            print(f"Error: {e}")
           
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Handle invalid request method
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request method. Only GET and POST are allowed.'}, status=405)









# Google Sheets setup
SERVICE_ACCOUNT_FILE = 'E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
SPREADSHEET_ID = '1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE'
RANGE_NAME = 'profile!A:AH'  # Adjusted to match columns A (Name), B (Email), C (Password), D (Gender)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def update_profile(request):
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        current_user = request.session.get('email')  # Retrieve the logged-in user's email
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if 'search' in request.POST:
            # Search by email
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
            rows = result.get('values', [])
            email_index = 1  # Email is in the 2nd column (0-based index)

            # Find the row with the matching email
            for i, row in enumerate(rows):
                if len(row) > email_index and row[email_index].strip() == email:
                    profile_data = {
                        'email': row[1],   # Email in Column 2
                        'name': row[0],    # Name in Column 1
                        'password': row[2], # Password in Column 3
                        'gender': row[3],   # Gender in Column 4
                        'birth_date':row[4],
                        'mobile_number':row[5],
                        'college_name':row[6],
                        'id_number':row[7],
                        'batch_number':row[8],
                        'city':row[9],
                        'address':row[10],
                        'state':row[11],
                        'country':row[12],
                        'qualification':row[13],
                        'role':row[14],
                        'language':row[15],
                        'skills':row[16],
                        'locations':row[17],
                        'bank_name':row[18],
                        'branch_name':row[19],
                        'ifsc_code':row[20],
                        'account_number':row[21],
                        'pan_number':row[22],
                        'gst_number':row[23],
                        'photo':row[24],
                        'certificate':row[25],
                        'resume':row[26],
                        'ready_to_relocate':row[27],
                        'experience':row[28],

                    }
                    return render(request, 'pages/profile-update.html', {'profile': profile_data})
            
            # If email is not found
            return render(request, 'pages/profile-update.html', {'error': "Email not found."})

        elif 'update_profile' in request.POST:
            # Update the spreadsheet
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
            rows = result.get('values', [])
            email_index = 1  # Email is in the 2nd column (0-based index)

            # Find the row with the matching email
            for i, row in enumerate(rows):
                if len(row) > email_index and row[email_index].strip() == email:
                    # Handle file uploads
                    fs = FileSystemStorage()

                    photo = request.FILES.get('photo')
                    certificate = request.FILES.get('certificate')
                    resume = request.FILES.get('resume')

                    # Save files to the respective folders
                    photo_url = fs.save(f"photos/{photo.name}", photo) if photo else row[24]
                    certificate_url = fs.save(f"certificates/{certificate.name}", certificate) if certificate else row[25]
                    resume_url = fs.save(f"resumes/{resume.name}", resume) if resume else row[26]



                    updated_data = [
                        request.POST.get('name', row[0]),  # Name
                        email,  # Email (unchanged)
                        request.POST.get('password', row[2]),  # Password
                        request.POST.get('gender', row[3]),  
                        request.POST.get('birth_date', row[4]),  
                        request.POST.get('mobile_number', row[5]), 
                        request.POST.get('college_name', row[6]),  
                        request.POST.get('id_number', row[7]),
                        request.POST.get('batch_number', row[8]),
                        request.POST.get('city', row[9]),
                        request.POST.get('address', row[10]),
                        request.POST.get('state', row[11]),
                        request.POST.get('country', row[12]),
                        request.POST.get('qualification', row[13]),
                        request.POST.get('role', row[14]),
                        request.POST.get('language', row[15]),
                        request.POST.get('skills', row[16]),
                        request.POST.get('locations', row[17]),
                        request.POST.get('bank_name', row[18]),
                        request.POST.get('branch_name', row[19]),
                        request.POST.get('ifsc_code', row[20]),
                        request.POST.get('account_number', row[21]),
                        request.POST.get('pan_number', row[22]),
                        request.POST.get('gst_number', row[23]),
                        photo_url,
                        certificate_url,
                        resume_url,
                        request.POST.get('ready_to_relocate', row[27]),
                        request.POST.get('experience', row[28]),
                        row[29] if len(row) > 29 else '',  # Column 1 after experience
                        row[30] if len(row) > 30 else '',  # Column 2 after experience
                        row[31] if len(row) > 31 else '',  # Column 3 after experience

                        current_user,  # Updated by (current logged-in user)
                        current_time  # Updated date


                    ]
                    range_to_update = f"profile!A{i+1}:AH{i+1}"
                    sheet.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=range_to_update,
                        valueInputOption='RAW',
                        body={"values": [updated_data]}
                    ).execute()
                    

                    return render(request, 'pages/profile-update.html', {'success': "Profile updated successfully!"})

    return render(request, 'pages/profile-update.html')








# Google Sheets API credentials and configuration
SERVICE_ACCOUNT_FILE = 'E:\\Theme+\\hud_django_v3.0\\template_django\\DjangoHUDApp\\credentials\\google_credentials.json'
SPREADSHEET_ID = '1yIixxRzO7rqG9Iey7r9zQfww-e89zwqpjBpb3TxE0fE'
RANGE_NAME = 'profile!A:AK'

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Function to update the last column of the profile in the Google Spreadsheet
def update_spreadsheet_for_delete(email, deleted_by):
    # Load the credentials
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Build the Google Sheets API service
    service = build('sheets', 'v4', credentials=credentials)

    # Get the data from the spreadsheet
    sheet = service.spreadsheets()

    # Read all the rows from the 'profile' sheet
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    # Find the row with the matching email and update the last column (30th column -> index 29)
    for i, row in enumerate(rows):
        if len(row) > 1 and row[1].strip() == email:  # Assuming email is in the second column (index 1)
            # Ensure the row has at least 30 columns (A-AD)
            while len(row) < 37:
                row.append('')  # Append empty values to the row until it has 30 columns

            # Update the last column (index 29) to '1'
            row[29] = '1'
            row[34] = deleted_by  # Set 'deleted_by' in the 35th column
            row[35] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Set 'deleted_date' in the 36th column
            
            # Update the row in the Google Sheets
            body = {
                'values': [row]
            }
            sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f'profile!A{i+1}:AK{i+1}', valueInputOption='RAW', body=body).execute()
            break

def profiledelete(request):
    # Check if email is provided in the request
    if request.method == 'POST' and request.POST.get('email'):
        email = request.POST['email']
        deleted_by = request.session.get('email')  # Get the logged-in user's email
        print(email)
        update_spreadsheet_for_delete(email, deleted_by)  # Update the last column for the profile

        # Return a success response or render a success message
        return render(request, "pages/profile-delete.html", {"success": f"Profile with email {email} has been deleted ."})
    
    return render(request, "pages/profile-delete.html")







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