from django.urls import path, include
from django.conf import settings
from django.utils.module_loading import import_string
from . import views as service_view
from .views import *

urlpatterns=[
	path("postshp/",service_view.Postshp.as_view()),
	#Server Urls
	path("GetServerList",service_view.GetServerList.as_view(),name="GetServerList"),
	path("PostServerApi",service_view.PostServerApi.as_view(),name="PostServerApi"),
	path("UpdateServerApi/<int:id>/",service_view.UpdateServerApi.as_view(),name="UpdateServerApi"),
	path("GetServer/<int:id>/",service_view.GetServer.as_view(),name="GetServer"),
	path("DeleteServer/<int:id>/",service_view.DeleteServer.as_view(),name="DeleteServer"),

	#Workspace Urls
	path("GetWorkspaceList",service_view.GetWorkspaceList.as_view(),name="GetWorkspaceList"),
	path("PostWorkspaceApi",service_view.PostWorkspaceApi.as_view(),name="PostWorkspaceApi"),
	path("UpdateWorkspaceApi/<int:id>/",service_view.UpdateWorkspaceApi.as_view(),name="UpdateWorkspaceApi"),
	path("GetWorkspace/<int:id>/",service_view.GetWorkspace.as_view(),name="GetWorkspace"),
	path("DeleteWorkspace/<int:id>/",service_view.DeleteWorkspace.as_view(),name="DeleteWorkspace"),

	#Datastore Urls
	path("GetDatastoreList",service_view.GetDatastoreList.as_view(),name="GetDatastoreList"),
	path("PostDatastoreApi",service_view.PostDatastoreApi.as_view(),name="PostDatastoreApi"),
	path("UpdateDatastoreApi/<int:id>/",service_view.UpdateDatastoreApi.as_view(),name="UpdateDatastoreApi"),
	path("GetDatastore/<int:id>/",service_view.GetDatastore.as_view(),name="GetDatastore"),
	path("DeleteDatastore/<int:id>/",service_view.DeleteDatastore.as_view(),name="DeleteDatastore"),

	#Layer Urls
	path("GetLayerList",service_view.GetLayerList.as_view(),name="GetLayerList"),
	path("GetDetailedLayerList",service_view.GetDetailedLayerList.as_view(),name="GetDetailedLayerList"),
	path("PostLayerApi",service_view.PostLayerApi.as_view(),name="PostLayerApi"),
	path("UpdateLayerApi/<int:id>/",service_view.UpdateLayerApi.as_view(),name="UpdateLayerApi"),
	path("GetLayer/<int:id>/",service_view.GetLayer.as_view(),name="GetLayer"),
	path("DeleteLayer/<int:id>/",service_view.DeleteLayer.as_view(),name="DeleteLayer"),


	#Layer Group Urls
	path("GetLayerGroupList",service_view.GetLayerGroupList.as_view(),name="GetLayerGroupList"),
	path("PostLayerGroupApi",service_view.PostLayerGroupApi.as_view(),name="PostLayerGroupApi"),
	path("UpdateLayerGroupApi/<int:id>/",service_view.UpdateLayerGroupApi.as_view(),name="UpdateLayerGroupApi"),
	path("GetLayerGroup/<int:id>/",service_view.GetLayerGroup.as_view(),name="GetLayerGroup"),
	path("DeleteLayerGroup/<int:id>/",service_view.DeleteLayerGroup.as_view(),name="DeleteLayerGroup"),


	#Gs Layers
	path("GetGsLayerList",service_view.GetGsLayerList.as_view(),name="GetGsLayerList"),
    
	path('PostShapeFile', PostShapeFile.as_view(), name=' Upload ZIP file in database'),
    path('GetShapeFiles', GetUploadedShapeFile.as_view(), name=' Get ZIP file'),
    path('DeleteshapeFolder/<str:folder_name>/', DeleteShapeFolder.as_view()),
]