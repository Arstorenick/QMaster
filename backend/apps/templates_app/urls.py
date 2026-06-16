from django.urls import path
from . import views

urlpatterns = [
    path('', views.template_list, name='template-list'),
    path('<int:template_id>/', views.template_detail, name='template-detail'),
    path('<int:template_id>/clone/', views.clone_template, name='template-clone'),
    path('add/<int:survey_id>/', views.add_to_template, name='template-add'),
]
