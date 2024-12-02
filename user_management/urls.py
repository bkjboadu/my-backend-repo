from django.urls import path
from user_management.views import *

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    # path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    # path(
    #     "google/login/callback/", GoogleCallbackView.as_view(), name="google_callback"
    # ),
    # path("google-auth/", GoogleAuthAPIView.as_view(), name="google_auth_api"),
    path("users/", UserLists.as_view(), name="lists"),
    path("activate/<str:token>/", Activate.as_view(), name="activate"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        PasswordResetConfirm.as_view(),
        name="passwordresetconfirm",
    ),
    path("password_change/", PasswordChange.as_view(), name="passwordchange"),
    path("profile_update/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("delete_account/", DeleteAccount.as_view(), name="delete"),
    path("activate/<token>/", Activate.as_view(), name="activate"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
