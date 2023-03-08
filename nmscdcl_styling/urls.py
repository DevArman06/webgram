from django.urls import path, include
from django.conf import settings
from django.utils.module_loading import import_string
from . import views as styling_view

urlpatterns=[
	path("PostStyleApi/<int:layer_id>/",styling_view.PostStyleApi.as_view(),name="PostStyleApi"),
	path("UpdateStyleApi/<int:layer_id>/<int:style_id>/",styling_view.UpdateStyleApi.as_view(),name="UpdateStyleApi"),

]