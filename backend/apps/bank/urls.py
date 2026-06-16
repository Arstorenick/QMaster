from django.urls import path
from . import views

urlpatterns = [
    path('', views.bank_list, name='bank-list'),
    path('<int:item_id>/import/<int:survey_id>/', views.bank_import, name='bank-import'),
]
