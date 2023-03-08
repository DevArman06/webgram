from django.shortcuts import render
from rest_framework import generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from .models import Style
from nmscdcl_services.models import Layer
from .serializers import PostStyleSerializer,GetStyleSerializer,UpdateStyleSerializer
from nmscdcl_services import geographic_servers
from .nmscdcl_custom_add import create_style,update_style

# Create your views here.

class PostStyleApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class = PostStyleSerializer
	parser_classes=[MultiPartParser]

	def post(self,request,layer_id,*args,**kwargs):

		serializer=self.get_serializer(data=request.data)

		if serializer.is_valid():
			style_name=serializer.validated_data["name"]
			style_title=serializer.validated_data["title"]
			is_default=serializer.validated_data["is_default"]
			sld=serializer.validated_data["sld"]
			try:
				layer=Layer.objects.get(pk=layer_id)
			except Layer.DoesNotExist as e:
				return Response({
					"message":"layer with id %s does not exists"%layer_id,
					"status":"error"
					})
			gs=geographic_servers.get_instance().get_server_by_id(layer.datastore.workspace.server.id)
			style=create_style(style_name,style_title,sld,is_default,layer,gs)
			if style:
				# gs.reload_node()
			# style=serializer.save()
				data=GetStyleSerializer(style,context=self.get_serializer_context()).data

				return Response({
					"message":"Style data saved successfully",
					"status":"success",
					"data":data
					})
			return Response({
				"message":"there is some issue",
				"status":"error"
				})
		return Response({
			"message":"Style data not saved successfully",
			"status":"error",
			"error":serializer.errors
			})


class UpdateStyleApi(generics.GenericAPIView):
	# permission_classes=[permissions.IsAuthenticated]
	serializer_class = UpdateStyleSerializer
	parser_classes=[MultiPartParser]

	def put(self,request,layer_id,style_id,*args,**kwargs):
		try:
			layer=Layer.objects.get(pk=layer_id)
		except Layer.DoesNotExist as e:
			return Response({
				"message":"layer with id %s does not exists"%(layer_id),
				"status":"error"
				})
		try:
			style=Style.objects.get(pk=style_id)
		except Style.DoesNotExist as e:
			return Response({
				"message":"style with id %s does not exists"%(style_id),
				"status":"error"
				})
		serializer=self.get_serializer(data=request.data,instance=style)
		if serializer.is_valid():

			style_name=serializer.validated_data["name"]
			is_default=serializer.validated_data["is_default"]
			sld=serializer.validated_data["sld"]

			gs=geographic_servers.get_instance().get_server_by_id(layer.datastore.workspace.server.id)

			updated_style=update_style(layer,style_name,sld,gs,style,is_default)

			if updated_style:
				style_data=serializer.save()

				data=GetStyleSerializer(style_data,context=self.get_serializer_context()).data

				return Response({
					"message":"Style data updated successfully",
					"status":"success",
					"data":data
					})
			else:
				return Response({
					"message":"there is some issue while updating the style data",
					"status":"error"
					})
		return Response({
			"message":"it tlooks like there is some validation error",
			"status":"error",
			"error":serializer.errors
			})