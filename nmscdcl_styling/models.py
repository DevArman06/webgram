from django.db import models
from nmscdcl_services.models import Layer
# Create your models here.


class Style(models.Model):
	name=models.CharField(max_length=100)
	title=models.CharField(max_length=120,blank=True,null=True)
	is_default=models.BooleanField(default=False)
	sld=models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name


class LayerStyle(models.Model):
	layer=models.ForeignKey(Layer,on_delete=models.CASCADE,related_name="styleLayer")
	style=models.ForeignKey(Style,on_delete=models.CASCADE,related_name="assignStyle")

	def __str__(self):
		return self.layer.name+"-"+self.style.name