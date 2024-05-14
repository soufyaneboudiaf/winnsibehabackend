from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
    TokenRefreshView)
from .views import register , search , reserveProduct , addProduct , addReview , addPicture

urlpatterns = [
    path("login/" , TokenObtainPairView.as_view() , name = 'token_obtain_pair'),
    path("register/" , register , name = 'register'),
    path("search/" , search , name = 'search'),
    path("reserveProduct/" , reserveProduct , name = 'reserveProduct'),
    path("addProduct/" , addProduct , name = 'addProduct'),
    path("addReview/" , addReview , name = 'addReview'),
    path("addPicture/" , addPicture , name = 'addPicture'),
    path("refresh/" , TokenRefreshView.as_view() , name = 'token_refresh'),
    # path("sign_in/" ,sign_in , name= 'sign_in')

]