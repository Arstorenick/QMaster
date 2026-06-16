from django.urls import path
from . import views

urlpatterns = [
    # Survey CRUD
    path('', views.survey_list, name='survey-list'),
    path('create/', views.survey_create, name='survey-create'),
    path('<int:survey_id>/', views.survey_detail, name='survey-detail'),
    path('<int:survey_id>/publish/', views.survey_publish, name='survey-publish'),
    path('<int:survey_id>/style/', views.survey_style, name='survey-style'),
    path('public/', views.public_list, name='survey-public-list'),
    path('<int:survey_id>/public/', views.survey_public, name='survey-public'),

    # Questions
    path('<int:survey_id>/questions/', views.question_list, name='question-list'),
    path('<int:survey_id>/questions/reorder/', views.question_reorder, name='question-reorder'),
    path('<int:survey_id>/questions/<int:question_id>/', views.question_detail, name='question-detail'),

    # Options
    path('<int:survey_id>/questions/<int:question_id>/options/', views.option_create, name='option-create'),
    path('<int:survey_id>/questions/<int:question_id>/options/<int:option_id>/', views.option_detail, name='option-detail'),
]
