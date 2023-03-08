from django.shortcuts import render
from django.shortcuts import render
from .models import SHP,Server,Workspace,Datastore,LayerGroup,Layer
from .serializers import PostShpSerializer,GetServerSerializer,PostServerSerializer,UpdateServerSerializer,\
GetWorkspaceSerializer,PostWorkspaceSerializer,UpdateWorkspaceSerializer,GetDatastoreSerializer,\
PostDatastoreSerializer,UpdateDatastoreSerializer,GetLayerSerializer,PostLayerSerializer,\
UpdateLayerSerializer,GetGsLayerSerializer,GetLayerGroupSerializer,PostLayerGroupSerializer,\
UpdateLayerGroupSerializer,GetShortLayerSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions,mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from django.db.models import Q
from django.contrib.auth.models import Group
from .backend_geoserver import exportShpToPostgis
from pathlib import Path
from osgeo import osr
import os
from sridentify import Sridentify
# import urllib.request as urllib2
import json
from urllib.parse import urlencode
from urllib.request import urlopen
# from django.conf.settings import DEFAULT_DB_STRUCTURE
from nmscdcl.settings import DEFAULT_DB_STRUCTURE
from .backend_geoserver import Geoserver
import json
from rest_framework.permissions import IsAuthenticated
from nmscdcl_auth.models import User
from .serializers import *
import io
import shutil
import zipfile
from nmscdcl import settings
# Create your views here.

def getprj(shp_path):
    prj_file=shp_path.replace('.shp','.prj').replace('.SHP','.prj')
    print(prj_file,"this is my prj file")
    if not os.path.isfile(prj_file):
        prj_file=prj_file.replace('.prj','.PRJ')
    print(prj_file)
    with open(prj_file,"r") as f:
        prj_text=f.read()
    srs=osr.SpatialReference()
    srs.ImportFromESRI([prj_text])
    print("Shape prj is : ",prj_text)
    print("wkt4 is : ",str(srs.ExportToWkt()))
    print("proj4 is : ",str(srs.ExportToProj4()))
    srs.AutoIdentifyEPSG()
    print("EPSG is : ",str(srs.GetAuthorityCode(None)))

    query=urlencode({
    	"exact":True,
    	"error":True,
    	"mode":'wkt',
    	"terms":prj_text
    	})

    webres=urlopen('http://prj2epsg.org/search.json',query.encode())
    jres=json.loads(webres.read().decode())
    print(jres)



class Postshp(generics.GenericAPIView):
	serializer_class=PostShpSerializer
	parser_classes=[MultiPartParser]

	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		print(request.FILES['file'])
		if serializer.is_valid():
			data=serializer.save()

			if len(Server.objects.all()) == 1:
				data.default=True
				data.save()
			elif len(Server.objects.all()) > 1:
				data.default=False
				data.save()

			data=PostShpSerializer(data).data
			# exportShpToPostgis(serializer.data)
			getprj("D:\\Projects BGIS\\NMSCDCL\\nmscdcl\\media\\tasmania\\tasmania_roads.shp")
			return Response({
				"message":"data reached successfully",
				"status":"success",
				"data":data,
				})
		return Response({
			"message":"failed",
			"status":"error",
			"error":serializer.errors
			})



"""
Server Api's
"""

class GetServerList(APIView):
	# permission_classes=[permissions.IsAuthenticated]
	
	def get(self,request,*args,**kwargs):
		server=Server.objects.all()
		data=GetServerSerializer(server,many=True).data

		if data:
			return Response({
			"message":"data fetched successfully",
			"status":"success",
			"data":data
			})
		return Response({
			"message":"there is no server data avialable",
			"status":"error",
			"data":data
			})


class PostServerApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=PostServerSerializer

	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		if serializer.is_valid():
			server=serializer.save()
			data=GetServerSerializer(server,context=self.get_serializer_context()).data
			return Response({
				"message":"Server data saved successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"Server data not saved",
			"status":"error",
			"error":serializer.errors
			})


class UpdateServerApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=UpdateServerSerializer

	def put(self,request,id,*args,**kwargs):
		try:
			instance=Server.objects.get(pk=id)
		except Server.DoesNotExist as e:
			return Response({
				"message":"server with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance)

		if serializer.is_valid():
			server=serializer.save()
			data=GetServerSerializer(server,context=self.get_serializer_context()).data

			return Response({
				"message":"server updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"server not updated",
			"status":"error",
			"error":serializer.errors
			})
	def patch(self,request,id,*args,**kwargs):
		try:
			instance=Server.objects.get(pk=id)
		except Server.DoesNotExist as e:
			return Response({
				"message":"server with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance,partial=True)

		if serializer.is_valid():
			server=serializer.save()
			data=GetServerSerializer(server,context=self.get_serializer_context()).data

			return Response({
				"message":"server updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"server not updated",
			"status":"error",
			"error":serializer.errors
			})

class GetServer(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def get(self,request,id,*args,**kwargs):

		try:
			instance=Server.objects.get(pk=id)
		except Server.DoesNotExist as e:
			return Response({
				"message":"server with id %s does not exists"%(id),
				"status":"error"
				})

		data=GetServerSerializer(instance).data

		return Response({
			"message":"server data fetched successfully",
			"status":"success",
			"data":data
			})


class DeleteServer(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def delete(self,request,id,*args,**kwargs):
		try:
			instance=Server.objects.get(pk=id)
		except Server.DoesNotExist as e:
			return Response({
				"message":"server with id %s does not exists"%(id),
				"status":"error"
				})
		instance.delete()

		return Response({
			"message":"server data deleted successfully",
			"status":"success"
			},status=status.HTTP_200_OK)




"""
Workspace Api's
"""

class GetWorkspaceList(APIView):
	# permission_classes=[permissions.IsAuthenticated]
	
	def get(self,request,*args,**kwargs):
		workspace=Workspace.objects.all()
		data=GetWorkspaceSerializer(workspace,many=True).data

		if data:
			return Response({
			"message":"data fetched successfully",
			"status":"success",
			"data":data
			})
		return Response({
			"message":"there is no workspace data avialable",
			"status":"error",
			"data":data
			})


class PostWorkspaceApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=PostWorkspaceSerializer

	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		if serializer.is_valid():
			# server_id=serializer.validated_data["server"]
			name=serializer.validated_data["name"]
			try:
				# server=Server.objects.get(pk=server_id)
				server=serializer.validated_data["server"]
			except Exception as e:
				return Response({
					"message":"server with id does not exists",
					"status":"error"
					})
			
			server_url=server.frontend_url
			services_dict={
			"uri":server.frontend_url+"/"+ name,
			"wms_endpoint":server.getWmsEndpoint(workspace=name),
			"wfs_endpoint":server.getWfsEndpoint(workspace=name),
			"wcs_endpoint":server.getWcsEndpoint(workspace=name),
			"wmts_endpoint":server.getWmtsEndpoint(workspace=name),
			"cache_endpoint":server.getCacheEndpoint(workspace=name)
			}
			workspace=serializer.save(**services_dict)
			data=GetWorkspaceSerializer(workspace,context=self.get_serializer_context()).data
			return Response({
				"message":"workspace data saved successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"workspace data not saved",
			"status":"error",
			"error":serializer.errors
			})


class UpdateWorkspaceApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=UpdateWorkspaceSerializer

	# def put(self,request,id,*args,**kwargs):
	# 	try:
	# 		instance=Workspace.objects.get(pk=id)
	# 	except Workspace.DoesNotExist as e:
	# 		return Response({
	# 			"message":"workspace with id %s does not exists"%(id),
	# 			"status":"error"
	# 			})
	# 	serializer=self.get_serializer(data=request.data,instance=instance)

	# 	if serializer.is_valid():
	# 		workspace=serializer.save()
	# 		data=GetWorkspaceSerializer(workspace,context=self.get_serializer_context()).data

	# 		return Response({
	# 			"message":"workspace updated successfully",
	# 			"status":"success",
	# 			"data":data
	# 			})
	# 	return Response({
	# 		"message":"workspace not updated",
	# 		"status":"error",
	# 		"error":serializer.errors
	# 		})
	def patch(self,request,id,*args,**kwargs):
		try:
			instance=Workspace.objects.get(pk=id)
		except Workspace.DoesNotExist as e:
			return Response({
				"message":"workspace with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance,partial=True)

		if serializer.is_valid():
			workspace=serializer.save()
			data=GetWorkspaceSerializer(workspace,context=self.get_serializer_context()).data

			return Response({
				"message":"workspace updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"workspace not updated",
			"status":"error",
			"error":serializer.errors
			})

class GetWorkspace(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def get(self,request,id,*args,**kwargs):

		try:
			instance=Workspace.objects.get(pk=id)
		except Workspace.DoesNotExist as e:
			return Response({
				"message":"workspace with id %s does not exists"%(id),
				"status":"error"
				})

		data=GetWorkspaceSerializer(instance).data

		return Response({
			"message":"workspace data fetched successfully",
			"status":"success",
			"data":data
			})


class DeleteWorkspace(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def delete(self,request,id,*args,**kwargs):
		try:
			instance=Workspace.objects.get(pk=id)
		except Workspace.DoesNotExist as e:
			return Response({
				"message":"workspace with id %s does not exists"%(id),
				"status":"error"
				})
		instance.delete()

		return Response({
			"message":"workspace data deleted successfully",
			"status":"success"
			},status=status.HTTP_200_OK)



"""
Datastore Api's
"""

class GetDatastoreList(APIView):
	# permission_classes=[permissions.IsAuthenticated]
	
	def get(self,request,*args,**kwargs):
		datastore=Datastore.objects.all()
		# datastore.connection_params["passwd"]="****"
		data=GetDatastoreSerializer(datastore,many=True).data

		if data:
			return Response({
			"message":"data fetched successfully",
			"status":"success",
			"data": data
			})
		return Response({
			"message":"there is no datastore data avialable",
			"status":"error",
			"data":data
			})


class PostDatastoreApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=PostDatastoreSerializer

	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		has_errors=False
		if not has_errors and serializer.is_valid():
			default_connection=("host","port","database","schema","user","passwd","dbtype")
			validate=lambda x:True if x in serializer.validated_data["connection_params"] else False
			connection_field_status=all(list(map(validate,default_connection)))
			if not bool(serializer.validated_data["connection_params"]) or not connection_field_status:
				return Response({
					"message":f"error in connection_params, There are some fields missing. connection_params should be like this {DEFAULT_DB_STRUCTURE}",
					"status":"error"
					})
				# created_by=request.user.name
			datastore=serializer.save()
			data=GetDatastoreSerializer(datastore,context=self.get_serializer_context()).data
			return Response({
				"message":"datastore data saved successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"datastore data not saved",
			"status":"error",
			"error":serializer.errors
			})


class UpdateDatastoreApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=UpdateDatastoreSerializer

	def put(self,request,id,*args,**kwargs):
		try:
			instance=Datastore.objects.get(pk=id)
		except Datastore.DoesNotExist as e:
			return Response({
				"message":"datastore with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance)

		if serializer.is_valid():
			datastore=serializer.save()
			data=GetDatastoreSerializer(datastore,context=self.get_serializer_context()).data

			return Response({
				"message":"datastore updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"datastore not updated",
			"status":"error",
			"error":serializer.errors
			})
	def patch(self,request,id,*args,**kwargs):
		try:
			instance=Datastore.objects.get(pk=id)
		except Datastore.DoesNotExist as e:
			return Response({
				"message":"datastore with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance,partial=True)

		if serializer.is_valid():
			datastore=serializer.save()
			data=GetDatastoreSerializer(datastore,context=self.get_serializer_context()).data

			return Response({
				"message":"datastore updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"datastore not updated",
			"status":"error",
			"error":serializer.errors
			})

class GetDatastore(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def get(self,request,id,*args,**kwargs):

		try:
			instance=Datastore.objects.get(pk=id)
			instance.connection_params["passwd"]="****"
		except Datastore.DoesNotExist as e:
			return Response({
				"message":"datastore with id %s does not exists"%(id),
				"status":"error"
				})

		data=GetDatastoreSerializer(instance).data

		return Response({
			"message":"datastore data fetched successfully",
			"status":"success",
			"data":data
			})


class DeleteDatastore(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def delete(self,request,id,*args,**kwargs):
		try:
			instance=Datastore.objects.get(pk=id)
		except Datastore.DoesNotExist as e:
			return Response({
				"message":"datastore with id %s does not exists"%(id),
				"status":"error"
				})
		instance.delete()

		return Response({
			"message":"datastore data deleted successfully",
			"status":"success"
			},status=status.HTTP_200_OK)




"""
LayerGroup Api's
"""

class GetLayerGroupList(APIView):
	# permission_classes=[permissions.IsAuthenticated]
	
	def get(self,request,*args,**kwargs):
		layergroup=LayerGroup.objects.all()
		data=GetLayerGroupSerializer(layergroup,many=True).data

		if data:
			return Response({
			"message":"data fetched successfully",
			"status":"success",
			"data":data
			})
		return Response({
			"message":"there is no layergroup data avialable",
			"status":"error",
			"data":data
			})


class PostLayerGroupApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=PostLayerGroupSerializer
	parser_classes=[MultiPartParser]

	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		if serializer.is_valid():
			try:
				Server.objects.get(pk=serializer.validated_data["server_id"])
			except Server.DoesNotExist as e:
				return Response({
					"message":"Enter proper server id",
					"status":"error"
					})
			layergroup=serializer.save()
			data=GetLayerSerializer(layergroup,context=self.get_serializer_context()).data
			return Response({
				"message":"layergroup data saved successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"layergroup data not saved",
			"status":"error",
			"error":serializer.errors
			})


class UpdateLayerGroupApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=UpdateLayerGroupSerializer
	parser_classes=[MultiPartParser]

	def put(self,request,id,*args,**kwargs):
		try:
			instance=LayerGroup.objects.get(pk=id)
		except LayerGroup.DoesNotExist as e:
			return Response({
				"message":"layer with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance)

		if serializer.is_valid():
			layergroup=serializer.save()
			data=GetLayerGroupSerializer(layergroup,context=self.get_serializer_context()).data

			return Response({
				"message":"layergroup updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"layergroup not updated",
			"status":"error",
			"error":serializer.errors
			})
	def patch(self,request,id,*args,**kwargs):
		try:
			instance=LayerGroup.objects.get(pk=id)
		except LayerGroup.DoesNotExist as e:
			return Response({
				"message":"layergroup with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance,partial=True)

		if serializer.is_valid():
			layergroup=serializer.save()
			data=GetLayerGroupSerializer(layergroup,context=self.get_serializer_context()).data

			return Response({
				"message":"layergroup updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"layergroup not updated",
			"status":"error",
			"error":serializer.errors
			})

class GetLayerGroup(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def get(self,request,id,*args,**kwargs):

		try:
			instance=LayerGroup.objects.get(pk=id)
		except LayerGroup.DoesNotExist as e:
			return Response({
				"message":"layergroup with id %s does not exists"%(id),
				"status":"error"
				})
		# print(instance.get_ol_params())

		data=GetLayerGroupSerializer(instance).data

		return Response({
			"message":"layergroup data fetched successfully",
			"status":"success",
			"data":data
			})


class DeleteLayerGroup(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def delete(self,request,id,*args,**kwargs):
		try:
			instance=LayerGroup.objects.get(pk=id)
		except LayerGroup.DoesNotExist as e:
			return Response({
				"message":"layergroup with id %s does not exists"%(id),
				"status":"error"
				})
		instance.delete()

		return Response({
			"message":"layergroup data deleted successfully",
			"status":"success"
			},status=status.HTTP_200_OK)






"""
Layer Api's
"""

class GetDetailedLayerList(APIView):
	# permission_classes=[permissions.IsAuthenticated]
	
	def get(self,request,*args,**kwargs):
		layer=Layer.objects.all()
		data=GetLayerSerializer(layer,many=True).data

		if data:
			return Response({
			"message":"data fetched successfully",
			"status":"success",
			"data":data
			})
		return Response({
			"message":"there is no layer data avialable",
			"status":"error",
			"data":data
			})


class GetLayerList(APIView):
	# permission_classes=[permissions.IsAuthenticated]
	
	def get(self,request,*args,**kwargs):
		layer=Layer.objects.values("id","name")
		data=GetShortLayerSerializer(layer,many=True).data

		if data:
			return Response({
			"message":"data fetched successfully",
			"status":"success",
			"data":data
			})
		return Response({
			"message":"there is no layer data avialable",
			"status":"error",
			"data":data
			})


class PostLayerApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=PostLayerSerializer
	parser_classes=[MultiPartParser]

	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		if serializer.is_valid():
			layer=serializer.save()
			data=GetLayerSerializer(layer,context=self.get_serializer_context()).data
			return Response({
				"message":"layer data saved successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"layer data not saved",
			"status":"error",
			"error":serializer.errors
			})


class UpdateLayerApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class=UpdateLayerSerializer
	parser_classes=[MultiPartParser]

	def put(self,request,id,*args,**kwargs):
		try:
			instance=Layer.objects.get(pk=id)
		except Layer.DoesNotExist as e:
			return Response({
				"message":"layer with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance)

		if serializer.is_valid():
			layer=serializer.save()
			data=GetLayerSerializer(layer,context=self.get_serializer_context()).data

			return Response({
				"message":"layer updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"layer not updated",
			"status":"error",
			"error":serializer.errors
			})
	
	def patch(self,request,id,*args,**kwargs):
		try:
			instance=Layer.objects.get(pk=id)
		except Layer.DoesNotExist as e:
			return Response({
				"message":"layer with id %s does not exists"%(id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=instance,partial=True)

		if serializer.is_valid():
			layer=serializer.save()
			data=GetLayerSerializer(layer,context=self.get_serializer_context()).data

			return Response({
				"message":"layer updated successfully",
				"status":"success",
				"data":data
				})
		return Response({
			"message":"layer not updated",
			"status":"error",
			"error":serializer.errors
			})

class GetLayer(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def get(self,request,id,*args,**kwargs):

		try:
			instance=Layer.objects.get(pk=id)
			print(instance)
		except Layer.DoesNotExist as e:
			return Response({
				"message":"layer with id %s does not exists"%(id),
				"status":"error"
				})
		# print(instance.get_ol_params())

		data=GetLayerSerializer(instance).data

		return Response({
			"message":"layer data fetched successfully",
			"status":"success",
			"data":data
			})


class DeleteLayer(APIView):
	# permission_classes=[permissions.IsAuthenticated]

	def delete(self,request,id,*args,**kwargs):
		try:
			instance=Layer.objects.get(pk=id)
		except Layer.DoesNotExist as e:
			return Response({
				"message":"layer with id %s does not exists"%(id),
				"status":"error"
				})
		instance.delete()

		return Response({
			"message":"layer data deleted successfully",
			"status":"success"
			},status=status.HTTP_200_OK)





"""
Temporary Get Layer Api
"""

class GetGsLayerList(generics.GenericAPIView):
	serializer_class=GetGsLayerSerializer
	def post(self,request,*args,**kwargs):
		serializer=self.get_serializer(data=request.data)
		if serializer.is_valid():
			workspace=serializer.validated_data["workspace"]
			gs=Geoserver(1,"default","geoserver","admin","geoserver","http://localhost:8080/geoserver","http://localhost:8080/geoserver")
			gs_data=gs.getGsLayers()
			layers=[]
			for lyr in gs_data:
				if workspace in lyr.name:
					layers.append({"extent":list(lyr.resource.native_bbox)[:-1],\
						"url":"http://localhost:8080/geoserver/wms",\
						"srs":lyr.resource.projection,\
						"params":{"LAYERS":lyr.name,'VERSION': '1.1.1',"STYLES": '','TILED': False}})
			if layers:
				return Response({
					"message":"successfully fetched layers data",
					"status":"success",
					"data":layers
					})
		return Response({
			"message":"layer data not fetched",
			"status":"error",
			"error":serializer.errors
			})
	



class PostShapeFile(generics.GenericAPIView):
    serializer_class = UploadShapeFileSerializer 
    permission_classes = [IsAuthenticated]    
    parser_classes = [MultiPartParser]

    def get_new_media_path(self, media_path):
        index = 1
        while os.path.exists(f"{media_path}_{index}"):
            index += 1
        return f"{media_path}_{index}"

    def post(self, request, format=None):

        if 'shape_file' not in request.FILES:
            return Response({"status": "error", 
                             "message": "No file uploaded."} , status=400)
        
        zip_file = request.FILES['shape_file']
        zip_filename = zip_file.name
        if not zip_filename.endswith('.zip'):
            return Response({"status": "error" ,
                             "message" : f" {zip_filename} - Uploaded File is not a zip file" })

        media_path = os.path.join(settings.MEDIA_ROOT/'shapefiles', zip_filename[:-4])

        # Check if media folder for extracted files already exists
        while os.path.exists(media_path):
            choice = request.data.get('choice')
            if choice == 'Overwrite':
                shutil.rmtree(media_path)
            elif choice == 'New':
                media_path = self.get_new_media_path(media_path)
            else:
                return Response({'message': 'Invalid choice. Please select Overwrite or New.'})

        # Extract the ZIP file to the media folder
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(media_path)
        folder_name = media_path.split('\\')[-1]
        
        serializer = storeshapefilePathSerializer(data = {'folder_name' : folder_name})
        if serializer.is_valid():
            serializer.save(user = request.user)

        return Response({'status':'success',
                        'message': f'{zip_filename} uploaded and extracted successfully.'})
    

    
class GetUploadedShapeFile(APIView):
    def get(self, request):
        try:
            instance = ShapeFiles.objects.all()
        except ShapeFiles.DoesNotExist as e:
            return Response({"status": "error", "message":'No data found'},status=400)
        
        serializer = GetShapeFileSerializer(instance , many = True).data
        return Response({'status':'success',
                        'message': 'data fetched successfully',
                        'data': serializer})



class DeleteShapeFolder(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, folder_name, format=None):
        media_path = os.path.join(settings.MEDIA_ROOT, 'shapefiles', folder_name)
        folder_name= media_path.split('\\')[-1]
        if os.path.exists(media_path):
            shutil.rmtree(media_path)
            ShapeFiles.objects.filter(folder_name=folder_name).delete()
            return Response({
                'status': 'success' , 
                'message': 'Folder deleted successfully.'})
        else:
            return Response({
                'status': 'error' , 
                'message': f'{folder_name} - This folder not found.'} , status=400)