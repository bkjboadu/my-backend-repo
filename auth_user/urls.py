from django.urls import path
from auth_user.views import (PasswordResetView, UserSignupView,UserLoginView,UserLists,
                          Activate, PasswordResetView, PasswordResetConfirm,PasswordChange,
                           DeleteAccount, LogoutView)
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('userlists/', UserLists.as_view(), name= 'lists'),
    path('activate/<str:token>/', Activate.as_view(), name='activate'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('passwordresetconfirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name= 'passwordresetconfirm'),
    path('password_change/', PasswordChange.as_view(), name= 'passwordchange'),
    path('delete_account/', DeleteAccount.as_view(), name= 'delete'),
    path('activate/<token>/', Activate.as_view(), name= 'activate'),
    path('logout/', LogoutView.as_view(), name='logout'),
]