from django.urls import path
from . import views

app_name = 'Accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('request_withdrawal/',views.request_withdrawal, name='request_withdrawal'),
    path('manage_withdrawals/',views.manage_withdrawals , name='manage_withdrawals'),
    path('approve_withdrawal/<int:withdrawal_id>/', views.approve_withdrawal, name='approve_withdrawal'),
    path('deny_withdrawal/<int:withdrawal_id>/', views.deny_withdrawal, name='deny_withdrawal'),
    path('check_unread_alerts/', views.check_unread_alerts, name='check_unread_alerts'),
    path('alerts/', views.user_alerts, name='user_alerts'),
    path('alerts/mark_as_read/<int:alert_id>/', views.mark_alert_as_read, name='mark_alert_as_read'),
]