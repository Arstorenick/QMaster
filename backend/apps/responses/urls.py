from django.urls import path
from . import views

urlpatterns = [
    path('<int:survey_id>/submit/', views.submit_survey, name='survey-submit'),
    path('<int:survey_id>/statistics/', views.survey_statistics, name='survey-statistics'),
    path('<int:survey_id>/statistics/export/', views.export_statistics, name='survey-export'),
    path('<int:survey_id>/questions/<int:question_id>/text-answers/', views.text_answers, name='text-answers'),
]
