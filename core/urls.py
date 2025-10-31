from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('audits/', views.audit_list_view, name='audit_list'),
    path('audits/create/', views.create_audit_view, name='create_audit'),
    path('audit/<int:pk>/', views.audit_detail_view, name='audit_detail'),
    path('audit/<int:pk>/publish/', views.publish_audit_view, name='publish_audit'),
    path('audit/<int:pk>/pdf/', views.audit_pdf_view, name='audit_pdf'),
    path('audit/<int:pk>/add-conclusion/', views.add_conclusion_view, name='add_conclusion'),
    
    # URLs pour le formulaire progressif
    path('audits/create/step1/', views.create_audit_step1, name='create_audit_step1'),
    path('audits/<int:pk>/step2/', views.audit_step2, name='audit_step2'),
    path('audits/<int:pk>/step3/', views.audit_step3, name='audit_step3'),
    path('audits/<int:pk>/step4/', views.audit_step4, name='audit_step4'),
    path('audits/<int:pk>/step5/', views.audit_step5, name='audit_step5'),
    path('audits/<int:pk>/step6/', views.audit_step6, name='audit_step6'),
    path('audits/<int:pk>/step7/', views.audit_step7, name='audit_step7'),
    path('audits/<int:pk>/step8/', views.audit_step8, name='audit_step8'),
    path('audits/<int:pk>/step9/', views.audit_step9, name='audit_step9'),
    path('audits/<int:pk>/step10/', views.audit_step10, name='audit_step10'),
    path('audits/<int:pk>/step11/', views.audit_step11, name='audit_step11'),
    path('audits/<int:pk>/step12/', views.audit_step12, name='audit_step12'),
    path('audits/<int:pk>/step13/', views.audit_step13, name='audit_step13'),
    path('audits/<int:pk>/step14/', views.audit_step14, name='audit_step14'),
    
    # URLs AJAX pour la suppression
    path('shareholders/<int:pk>/delete/', views.delete_shareholder, name='delete_shareholder'),
    path('branches/<int:pk>/delete/', views.delete_branche, name='delete_branche'),
    path('managers/<int:pk>/delete/', views.delete_manager, name='delete_manager'),
    
    # URL pour appliquer la signature
    path('audit/<int:pk>/apply-signature/', views.apply_signature_view, name='apply_signature'),
]