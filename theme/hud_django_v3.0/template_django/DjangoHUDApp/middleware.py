from django.shortcuts import redirect

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that don't require authentication
        public_paths = ['/page/login/', '/', '/profile/add/', '/page/landing/' ,'/profile/update/','/profile/delete/','/index/']

        # Check if the path is public
        if request.path not in public_paths and not request.session.get('email'):
            return redirect('DjangoHUDApp:pageLogin')
        
        return self.get_response(request)
