from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.csrf_view, name='auth-csrf'),
    path('register/', views.register_view, name='auth-register'),
    path('login/', views.login_view, name='auth-login'),
    path('logout/', views.logout_view, name='auth-logout'),
    path('me/', views.me_view, name='auth-me'),
    path('profile/', views.profile_view, name='auth-profile'),
    path('change-password/', views.change_password, name='auth-change-password'),
    path('departments/', views.department_list, name='department-list'),
    path('departments/flat/', views.department_flat_list, name='department-flat'),
    path('departments/<int:dept_id>/', views.department_detail, name='department-detail'),
    path('departments/import/', views.batch_import, name='dept-import'),
    path('departments/dashboard/', views.dept_dashboard, name='dept-dashboard'),
    path('departments/survey-stats/<int:survey_id>/', views.dept_survey_stats, name='dept-survey-stats'),
    path('users/<int:user_id>/', views.admin_update_user, name='admin-update-user'),
    path('users/bulk-update-role/', views.admin_bulk_update_role, name='admin-bulk-update-role'),
    path('users/bulk-update-dept/', views.admin_bulk_update_dept, name='admin-bulk-update-dept'),
]
