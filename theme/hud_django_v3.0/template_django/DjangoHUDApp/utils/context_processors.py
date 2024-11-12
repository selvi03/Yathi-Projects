from django.urls import resolve

def mark_active_link(menu, current_path_name):
    for item in menu:
        item['is_active'] = item.get('name', '') == current_path_name

        if 'children' in item:
            item['children'] = mark_active_link(item['children'], current_path_name)

            if any(child.get('is_active', False) for child in item['children']):
                item['is_active'] = True

    return menu

def sidebar_menu(request):
	sidebar_menu = [{
		'text': 'Navigation',
		'is_header': 1
	},{
		'url': '/',
		'icon': 'bi bi-cpu',
		'text': 'Dashboard',
		'name': 'index'
	}, {
		'url': '/analytics',
		'icon': 'bi bi-bar-chart',
		'text': 'Analytics',
		'name': 'analytics'
	}, {
		'icon': 'bi bi-envelope',
		'text': 'Email',
		'children': [{
			'url': '/email/inbox',
			'action': 'Inbox',
			'text': 'Inbox',
			'name': 'emailInbox'
		}, {
			'url': '/email/compose',
			'action': 'Compose',
			'text': 'Compose',
			'name': 'emailCompose'
		}, {
			'url': '/email/detail',
			'action': 'Detail',
			'text': 'Detail',
			'name': 'emailDetail'
		}]
	}, {
		'is_divider': 1
	}, {
		'text': 'Components',
		'is_header': 1
	}, {
		'url': '/widgets',
		'icon': 'bi bi-columns-gap',
		'text': 'Widgets',
		'name': 'widgets'
	}, {
		'icon': 'bi bi-bag-check',
		'text': 'POS System',
		'children': [{
			'url': '/pos/customer-order',
			'text': 'Customer Order',
			'name': 'posCustomerOrder'
		}, {
			'url': '/pos/kitchen-order',
			'text': 'Kitchen Order',
			'name': 'posKitchenOrder'
		}, {
			'url': '/pos/counter-checkout',
			'text': 'Counter Checkout',
			'name': 'posCounterCheckout'
		}, {
			'url': '/pos/table-booking',
			'text': 'Table Booking',
			'name': 'posTableBooking'
		}, {
			'url': '/pos/menu-stock',
			'text': 'Menu Stock',
			'name': 'posMenuStock'
		}]
	}, {
		'icon': 'fa fa-heart',
		'text': 'UI Kits',
		'children': [{
			'url': '/ui/bootstrap',
			'text': 'Bootstrap',
			'name': 'uiBootstrap'
		}, {
			'url': '/ui/buttons',
			'text': 'Buttons',
			'name': 'uiButtons'
		}, {
			'url': '/ui/card',
			'text': 'Card',
			'name': 'uiCard'
		}, {
			'url': '/ui/icons',
			'text': 'Icons',
			'name': 'uiIcons'
		}, {
			'url': '/ui/modal-notifications',
			'text': 'Modal & Notifications',
			'name': 'uiModalNotifications'
		}, {
			'url': '/ui/typography',
			'text': 'Typography',
			'name': 'uiTypography'
		}, {
			'url': '/ui/tabs-accordions',
			'text': 'Tabs & Accordions',
			'name': 'uiTabsAccordions'
		}]
	}, {
		'icon': 'bi bi-pen',
		'text': 'Forms',
		'children': [{
			'url': '/form/elements',
			'text': 'Form Elements',
			'name': 'formElements'
		}, {
			'url': '/form/plugins',
			'text': 'Form Plugins',
			'name': 'formPlugins'
		}, {
			'url': '/form/wizards',
			'text': 'Wizards',
			'name': 'formWizards'
		}]
	}, {
		'icon': 'bi bi-grid-3x3',
		'text': 'Tables',
		'children': [{
			'url': '/table/elements',
			'text': 'Table Elements',
			'name': 'tableElements'
		},
		{
			'url': '/table/plugins',
			'text': 'Table Plugins',
			'name': 'tablePlugins'
		}]
	}, {
		'icon': 'bi bi-pie-chart',
		'text': 'Charts',
		'children': [{
			'url': '/chart/js',
			'text': 'Chart.js',
			'name': 'chartJs'
		},{
			'url': '/chart/apex',
			'text': 'Apexcharts.js',
			'name': 'chartApex'
		}]
	}, {
		'url': '/map',
		'icon': 'bi bi-compass',
		'text': 'Map',
		'name': 'map'
	}, {
		'url': 'Layout',
		'icon': 'bi bi-layout-sidebar',
		'text': 'Layout',
		'children': [{
			'url': '/layout/starter',
			'text': 'Starter Page',
			'name': 'layoutStarter'
		}, {
			'url': '/layout/fixed-footer',
			'text': 'Fixed Footer',
			'name': 'layoutFixedFooter'
		}, {
			'url': '/layout/full-height',
			'text': 'Full Height',
			'name': 'layoutFullHeight'
		}, {
			'url': '/layout/full-width',
			'text': 'Full Width',
			'name': 'layoutFullWidth'
		}, {
			'url': '/layout/boxed-layout',
			'text': 'Boxed Layout',
			'name': 'layoutBoxedLayout'
		}, {
			'url': '/layout/collapsed-sidebar',
			'text': 'Collapsed Sidebar',
			'name': 'layoutCollapsedSidebar'
		}, {
			'url': '/layout/top-nav',
			'text': 'Top Nav',
			'name': 'layoutTopNav'
		}, {
			'url': '/layout/mixed-nav',
			'text': 'Mixed Nav',
			'name': 'layoutMixedNav'
		}, {
			'url': '/layout/mixed-nav-boxed-layout',
			'text': 'Mixed Nav Boxed Layout',
			'name': 'layoutMixedNavBoxedLayout'
		}]
	}, {
		'icon': 'bi bi-collection',
		'text': 'Pages',
		'children': [{
			'url': '/page/scrum-board',
			'text': 'Scrum Board',
			'name': 'pageScrumBoard'
		}, {
			'url': '/page/product',
			'text': 'Products',
			'name': 'pageProduct'
		}, {
			'url': '/page/product-details',
			'text': 'Product Details',
			'name': 'pageProductDetails'
		}, {
			'url': '/page/order',
			'text': 'Orders',
			'name': 'pageOrder'
		}, {
			'url': '/page/order-details',
			'text': 'Order Details',
			'name': 'pageOrderDetails'
		}, {
			'url': '/page/gallery',
			'text': 'Gallery',
			'name': 'pageGallery'
		}, {
			'url': '/page/search-results',
			'text': 'Search Results',
			'name': 'pageSearchResults'
		}, {
			'url': '/page/coming-soon',
			'text': 'Coming Soon Page',
			'name': 'pageComingSoon'
		}, {
			'url': '/page/error',
			'text': 'Error Page',
			'name': 'pageError'
		}, {
			'url': '/page/login',
			'text': 'Login',
			'name': 'pageLogin'
		}, {
			'url': '/page/register',
			'text': 'Register',
			'name': 'pageRegister'
		}, {
			'url': '/page/messenger',
			'text': 'Messenger',
			'name': 'pageMessenger'
		}, {
			'url': '/page/data-management',
			'text': 'Data Management',
			'name': 'pageDataManagement'
		}, {
			'url': '/page/file-manager',
			'text': 'File Manager',
			'name': 'pageFileManager'
		}, {
			'url': '/page/pricing',
			'text': 'Pricing Page',
			'name': 'pagePricing'
		}]
	}, {
		'url': '/landing',
		'icon': 'bi bi-diagram-3',
		'text': 'Landing Page',
		'name': 'landing'
	}, {
		'is_divider': 1
	}, {
		'text': 'Users',
		'is_header': 1
	}, {
		'url': '/profile',
		'icon': 'bi bi-people',
		'text': 'Profile',
		'name': 'profile'
	}, {
		'url': '/calendar',
		'icon': 'bi bi-calendar4',
		'text': 'Calendar',
		'name': 'calendar'
	}, {
		'url': '/settings',
		'icon': 'bi bi-gear',
		'text': 'Settings',
		'name': 'settings'
	}, {
		'url': '/helper',
		'icon': 'bi bi-gem',
		'text': 'Helper',
		'name': 'helper'
	}]
	
	resolved_path = resolve(request.path_info)

	current_path_name = resolved_path.url_name
	
	sidebar_menu = mark_active_link(sidebar_menu, current_path_name)

	return {'sidebar_menu': sidebar_menu}