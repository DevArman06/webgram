"""nmscdcl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import settings
from django.conf.urls.static import static
from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

#Setting up the swagger documentation for NMSCDCL API
schema_view = swagger_get_schema_view(
   openapi.Info(
      title="WEB GRAM 2.0",
      default_version='2.0',
      description="This is an WebGIS application",
      contact=openapi.Contact(email="testing@api.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

NMSCDCL_URL_PREFIX= settings.NMSCDCL_PATH + '/'

urlpatterns = [
    path(NMSCDCL_URL_PREFIX+'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(NMSCDCL_URL_PREFIX+'docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(NMSCDCL_URL_PREFIX, include([
        path('admin/', admin.site.urls),
        ])),
]
if 'nmscdcl_auth.apps.NmscdclAuthConfig' in settings.INSTALLED_APPS:
    urlpatterns +=[
        path(NMSCDCL_URL_PREFIX+'auth/',include('nmscdcl_auth.urls'))
    ]

if 'nmscdcl_core.apps.NmscdclCoreConfig' in settings.INSTALLED_APPS:
    urlpatterns +=[
        path(NMSCDCL_URL_PREFIX+'core/',include('nmscdcl_core.urls')),
    ]

if 'nmscdcl_services.apps.NmscdclServicesConfig' in settings.INSTALLED_APPS:
    urlpatterns +=[
        path(NMSCDCL_URL_PREFIX+'services/',include('nmscdcl_services.urls'))
    ]

if 'nmscdcl_styling.apps.NmscdclStylingConfig' in settings.INSTALLED_APPS:
    urlpatterns +=[
        path(NMSCDCL_URL_PREFIX+'styling/',include('nmscdcl_styling.urls'))
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
