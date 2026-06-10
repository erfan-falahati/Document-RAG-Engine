from django.urls import path
from . import views

urlpatterns = [
    # Document Endpoints
    path('documents/upload/', views.api_upload_document, name='api_upload_document'),
    path('documents/<int:pk>/', views.api_delete_document, name='api_delete_document'),
    path('documents/update/<int:pk>/', views.api_update_document, name='api_update_document'),

    # QA Endpoints
    path('qa/ask/', views.api_ask_question, name='api_ask_question'),
    path('qa/<int:pk>/', views.api_manage_question, name='api_manage_question'),
]
