from rest_framework import serializers
from .models import *


class GetStyleSerializer(serializers.ModelSerializer):

	class Meta:
		model=Style
		fields=("id","name","title","is_default")


class PostStyleSerializer(serializers.ModelSerializer):

	class Meta:
		model=Style
		fields=("name","title","is_default","sld")

	def validate(self,validated_data):
		if "name" not in validated_data or validated_data["name"]=="":
			raise serializers.ValidationError("name cannot be empty")
		if "sld" not in validated_data or validated_data["sld"]=="":
			raise serializers.ValidationError("sld cannot be empty")

		return validated_data

class UpdateStyleSerializer(serializers.ModelSerializer):

	class Meta:
		model=Style
		fields=("name","title","is_default","sld")