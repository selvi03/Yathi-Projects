from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse
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
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import Profile
from datetime import datetime
from .models import Profile, LoginLogoutEvent

logger = logging.getLogger(__name__)

@csrf_protect
def organization_data_list(request):
    fields = [
        'org_name', 'spoc_name', 'designation', 'phone_no', 'email',
        'address', 'location', 'website', 'source_data', 'status',
        'feedback', 'remark', 'reference', 'callback_date',
        'initiated_date', 'followup_date'
    ]

    def update_field(instance_id, field_name, field_value):
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

    def delete_record(request, instance_id):
        """
        Delete a record from the OrganizationDataAlt model based on the given instance_id.

        Args:
            request (HttpRequest): The HTTP request object.
            instance_id (int): The ID of the instance to delete.

        Returns:
            JsonResponse: A response indicating the success or failure of the delete operation.
        """
        try:
            # Log the attempt to delete the record
            logger.info(f'Attempting to delete record with ID: {instance_id}')

            # Fetch the record based on the instance_id
            org_data = OrganizationDataAlt.objects.get(id=instance_id)

            # Log if the record is found and about to be deleted
            logger.info(f'Found record with ID: {instance_id}. Proceeding with deletion.')

            # Delete the record
            org_data.delete()

            # Log the successful deletion
            logger.info(f'Successfully deleted record with ID: {instance_id}')

            # Return a success response
            return JsonResponse({'success': True, 'message': 'Record deleted successfully.'})

        except OrganizationDataAlt.DoesNotExist:
            # Log error if record is not found
            logger.error(f'Instance with ID {instance_id} does not exist.')

            # Return a failure response with appropriate error message
            return JsonResponse({'success': False, 'message': 'Instance not found'}, status=404)

        except Exception as e:
            # Log any unexpected errors
            logger.error(f'Error deleting record with ID {instance_id}: {str(e)}')

            # Return a failure response with the error message
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    if request.method == "POST":
        if 'field_name' in request.POST:
            # Handle field update
            field_name = request.POST.get('field_name')
            field_value = request.POST.get('field_value')
            instance_id = request.POST.get('instance_id')

            if field_name in fields:
                return update_field(instance_id, field_name, field_value)
            else:
                logger.warning('Invalid field name attempted: %s', field_name)
                return JsonResponse({'success': False, 'message': 'Invalid field name'}, status=400)

        elif 'delete_id' in request.POST:
            # Handle record deletion
            instance_id = request.POST.get('delete_id')
            return delete_record(request, instance_id)

        else:
            # Handle form submission for adding or updating data
            instance_id = request.POST.get('instance_id')
            if instance_id:
                try:
                    org_data = OrganizationDataAlt.objects.get(id=instance_id)
                    form = OrganizationDataForm(request.POST, instance=org_data)
                except OrganizationDataAlt.DoesNotExist:
                    logger.error('Instance not found for ID: %s', instance_id)
                    return JsonResponse({'success': False, 'message': 'Instance not found'}, status=404)
            else:
                form = OrganizationDataForm(request.POST)

            logger.info('Form data: %s', request.POST)

            if form.is_valid():
                org_data = form.save(commit=False)
                status = form.cleaned_data.get('status')

                # Debugging logs to verify form data
                logger.info("Status received: %s", status)
                logger.info("callback_date in form data: %s", form.cleaned_data.get('callback_date'))
                logger.info("initiated_date in form data: %s", form.cleaned_data.get('initiated_date'))
                logger.info("followup_date in form data: %s", form.cleaned_data.get('followup_date'))

                # Ensure specific date fields are set based on status
                if status == 'callback':
                    org_data.callback_date = form.cleaned_data.get('callback_date')
                else:
                    org_data.callback_date = None

                if status == 'initiated':
                    org_data.initiated_date = form.cleaned_data.get('initiated_date')
                else:
                    org_data.initiated_date = None

                if status == 'follow_up':
                    org_data.followup_date = form.cleaned_data.get('followup_date')
                else:
                    org_data.followup_date = None

                try:
                    org_data.save()
                    logger.info('Data saved successfully for ID: %s', org_data.id)
                    return redirect('DjangoHUDApp:organization-data-list')
                except Exception as e:
                    logger.error('Error saving main form data: %s', str(e))
                    return JsonResponse({'success': False, 'message': 'Error saving data'}, status=500)
            else:
                logger.error('Form validation failed: %s', form.errors)
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:  # GET request: Render form and data
        form = OrganizationDataForm()
        data = OrganizationDataAlt.objects.all()
        context = {
            'form': form,
            'data': data,
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
                # Use user-provided date or default to None
                org_data.callback_date = form.cleaned_data.get('callback_date')
            elif status == 'initiated':
                org_data.initiated_date = form.cleaned_data.get('initiated_date')
            elif status == 'follow up':
                org_data.followup_date = form.cleaned_data.get('followup_date')

            # Save the organization data
            org_data.save()

            # Redirect to the list view after saving
            return redirect('DjangoHUDApp:placement_training')
    else:
        form = PlacementTrainingForm()

    # Fetch existing data to display in the template
    data = PlacementTraining.objects.all()
    return render(request, 'pages/placement_training.html', {'form': form, 'data': data})


def training_data_view(request):
    if request.method == 'POST':
        form = TrainingDataForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new training data
            return redirect('DjangoHUDApp:training_data')  # Redirect to the same page after submission
    else:
        form = TrainingDataForm()  # Create a new instance of the form

    # Fetch existing training data to display
    data = TrainingData.objects.all()  # Adjust based on your model

    return render(request, 'pages/training_data.html', {'form': form, 'data': data})

def corporate_training_view(request):
    if request.method == 'POST':
        form = CorporateTrainingForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new training data
            return redirect('DjangoHUDApp:corporate_training')  # Redirect to the same page after submission
    else:
        form = CorporateTrainingForm()  # Create a new instance of the form

    # Fetch existing training data to display
    data = CorporateTraining.objects.all()  # Adjust based on your model

    return render(request, 'pages/corporate-training.html', {'form': form, 'data': data})

def pageadmin(request):
    context = {
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0'
    }
    return render(request, "pages/page-admin.html", context)


from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Profile, LoginLogoutEvent

def pageLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Check if the profile exists with the given email and password
            profile = Profile.objects.get(email=email, password=password)

            # Create a login event
            LoginLogoutEvent.objects.create(profile=profile, event_type='login')

            # Store user id in session
            request.session['user_id'] = profile.id
            messages.success(request, "Login successful!")
            return redirect('DjangoHUDApp:landing')
        except Profile.DoesNotExist:
            messages.error(request, "Invalid email or password. Please try again.")

    context = {
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0'
    }
    return render(request, "pages/page-login.html", context)

def logout(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        try:
            profile = Profile.objects.get(id=user_id)

            # Create a logout event
            LoginLogoutEvent.objects.create(profile=profile, event_type='logout')

            # Clear the user id from session
            del request.session['user_id']
            messages.success(request, "You have been logged out successfully.")
        except Profile.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect('DjangoHUDApp:landing')


def index(request):
    return render(request, "pages/index.html") 


from .forms import ProfileForm


def profileadd(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile added successfully.')
            return redirect('DjangoHUDApp:landing')  # Redirect to another page after successful save
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm()

    context = {
        'form': form,
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0'
    }
    
    return render(request, 'pages/profile-add.html', context)






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






def profiledelete(request):
    context = {
        "appSidebarHide": 1,
        "appHeaderHide": 1,
        "appContentClass": 'p-0'
    }
    return render(request, "pages/profile-delete.html", context)





# def pageRegister(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')
#         country = request.POST.get('country')
#         gender = request.POST.get('gender')
#         birth_month = request.POST.get('birth_month')
#         birth_day = request.POST.get('birth_day')
#         birth_year = request.POST.get('birth_year')

#         if password != confirm_password:
#             messages.error(request, "Passwords do not match!")
#         else:
#             date_of_birth = f"{birth_year}-{birth_month}-{birth_day}"
#             UserRegistration.objects.create(
#                 name=name, email=email, password=password,
#                 country=country, gender=gender, date_of_birth=date_of_birth
#             )
#             messages.success(request, "Registration successful! Please log in.")
#             return redirect('DjangoHUDApp:pageLogin')

#     context = {
#         "appSidebarHide": 1,
#         "appHeaderHide": 1,
#         "appContentClass": 'p-0'
#     }
#     return render(request, "pages/page-register.html", context)



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

def landing(request):
	context = {
		"appSidebarHide": 1,
		"appHeaderHide": 1,
		"appContentClass": 'p-0'
	}
	return render(request, "pages/landing.html", context)

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