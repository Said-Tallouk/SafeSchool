from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/',          views.LoginView.as_view(),         name='login'),
    path('register/',       views.RegisterView.as_view(),      name='register'),
    path('token/refresh/',  TokenRefreshView.as_view(),        name='token_refresh'),
    path('me/',             views.MeView.as_view(),            name='me'),
    path('forgot-password/',       views.ForgotPasswordView.as_view(),  name='forgot_password'),
    path('verify-code/',           views.VerifyCodeView.as_view(),      name='verify_code'),
    path('reset-password/',        views.ResetPasswordView.as_view(),   name='reset_password'),
    path('upload-photo/',          views.UploadPhotoView.as_view(),     name='upload_photo'),
]
