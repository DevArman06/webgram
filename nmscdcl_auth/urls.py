from django.urls import path, include
from django.conf import settings
from django.utils.module_loading import import_string
from . import views as auth_views
from rest_framework_simplejwt import views as jwt_views


LOGIN_VIEW=import_string(getattr(settings,"NMSCDCL_LOGIN_VIEW","nmscdcl_auth.views.UserLogin"))
# LOGOUT_VIEW=import_string(getattr(settings,"NMSCDCL_LOGOUT_VIEW","nmscdcl_auth.views.UserLogout"))
REGISTER_VIEW=import_string(getattr(settings,"NMSCDCL_REGISTER_VIEW","nmscdcl_auth.views.UserRegister"))

NMSCDCL_AUTH_BACKEND=getattr(settings,"NMSCDCL_AUTH_BACKEND","nmscdcl_auth")

if NMSCDCL_AUTH_BACKEND == "nmscdcl_auth":
	AUTH_PATHS=[
		path("login/",LOGIN_VIEW.as_view(),name="User_login"),
		# path("logout/",LOGOUT_VIEW.as_view(),name="User_logout"),
		path("register/",REGISTER_VIEW.as_view(),name="User_registeration")
	]
else:
	AUTH_PATHS=[path("",include(NMSCDCL_AUTH_BACKEND + ".urls"))]


urlpatterns=AUTH_PATHS + [
	path("test/",auth_views.Test.as_view(),name="test"),
	# path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]