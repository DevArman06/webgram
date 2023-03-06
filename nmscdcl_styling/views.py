from django.shortcuts import render
from rest_framework import generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from .models import Style
from nmscdcl_services.models import Layer
from .serializers import PostStyleSerializer,GetStyleSerializer,UpdateStyleSerializer
from nmscdcl_services import geographic_servers
from .nmscdcl_custom_add import create_style

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