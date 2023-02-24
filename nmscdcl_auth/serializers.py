from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate

class UserRegisterSerializer(serializers.ModelSerializer):
	password=serializers.CharField(max_length=20)
	group=serializers.CharField(max_length=50,required=False)
	class Meta:
		model=User
		fields=["name","username","password","email","group"]
		extra_kwargs={"password": {"write_only": True}}

	def validate(self,data):
		if "name" not in data or data["name"]=="":
			raise ValidationError("name cannnot be empty")
		if "email" not in data or data["email"]=="":
			raise ValidationError("email cannnot be empty")
		if "username" not in data or data["username"]=="":
			raise ValidationError("username cannnot be empty")
		if "password" not in data or data["password"]=="":
			raise ValidationError("password cannnot be empty")
		return data

	def create(self,validated_data):
		user=User.objects.create_user(name=validated_data["name"],email=validated_data["email"],
			username=validated_data["username"],password=validated_data["password"])
		return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model=User
		fields=["name","username","email","groups"]
		read_only_fields=fields


class UserLoginSerializer(serializers.ModelSerializer):
	username=serializers.CharField(max_length=20)
	class Meta:
		model=User
		fields=["username","password"]
		extra_kwargs={"password":{"write_only":True}}

	def validate(self,data):
		if "username" not in data or data["username"]=="":
			raise ValidationError("username cannnot be empty")
		if "password" not in data or data["password"]=="":
			raise ValidationError("password cannnot be empty")
		user = authenticate(username=data["username"], password=data["password"])
		if user is not None:
			return user
		else:
			raise ValidationError("Invalid credentials!")
