from django.shortcuts import redirect


class AdminAccessMiddleware:
    """限制 /admin/ 仅总管理（role=1）可访问"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.path.startswith('/admin/login/'):
            if not request.user.is_authenticated:
                return redirect('/admin/login/?next=' + request.path)
            if not request.user.is_super_admin:
                return redirect('/')
        return self.get_response(request)
