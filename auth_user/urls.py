from django.urls import path
from auth_user.views import (UserSignupView,UserLoginView,UserLists,
                          Activate)
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('userlists/', UserLists.as_view(), name= 'lists'),
    path('activate/<token>/', Activate.as_view(), name= 'activate'),
]