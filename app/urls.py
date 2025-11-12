from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",views.index, name="index"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("signup/", views.sign, name="sign"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), 
         name='password_reset'),

    # Success page after submitting email
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

    # Reset link with token (from email)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),

    # Final success page after password is reset
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),


     path("checkout/<str:plan_name>/", views.create_checkout_session, name="create_checkout_session"),
     path("success/", views.success_view, name="success"),
     path("cancel/", views.cancel_view, name="cancel"),


     path('api/chat/', views.smart_chat_view, name='smart_chat_api'),
]  
# template_name='registration/password_reset_confirm.html'
# template_name='registration/password_reset_complete.html'