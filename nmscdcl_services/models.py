from django.db import models
# from django.contrib.postgres.fields import JSONField
from django.conf import settings
from .backend_postgis import Introspect
from django.utils.crypto import get_random_string

# Create your models here.

CLONE_PERMISSION_CLONE = "clone"
CLONE_PERMISSION_SKIP = "skip"


class SHP(models.Model):
	file=models.FileField(upload_to="shp/")
	mode=models.CharField(max_length=20)
	name=models.CharField(max_length=20)
	encoding=models.CharField(max_length=20)
	srs=models.TextField()
	connection_params=models.JSONField(blank=True,null=True)


class Server(models.Model):
	TYPE_CHOICES=(
		("geoserver","geoserver"),
		("mapserver","mapserver"))

	name = models.CharField(max_length=100, unique=True)
	title = models.CharField(max_length=100, null=True, blank=True)
	description = models.CharField(max_length=500, null=True, blank=True)
	type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='geoserver')
	frontend_url = models.CharField(max_length=500)
	user = models.CharField(max_length=25)
	password = models.CharField(max_length=100)
	default = models.BooleanField(default=False)
	is_delete=models.BooleanField(default=False)
	timestamp=models.DateTimeField(auto_now=True)

	def _get_relative_url(self, url):
		if url.startswith(settings.BASE_URL + '/'):
			return url[len(settings.BASE_URL):]
		return url

	def getWmsEndpoint(self, workspace=None, relative=False):
		if relative:
			base_url =  self._get_relative_url(self.frontend_url)
		else:
			base_url = self.frontend_url
		if workspace:
			return base_url + "/" + workspace + "/wms"
		return base_url + "/wms"

	def getWfsEndpoint(self, workspace=None, relative=False):
		if relative:
			base_url =  self._get_relative_url(self.frontend_url)
		else:
			base_url = self.frontend_url
		if workspace:
			return base_url + "/" + workspace + "/wfs"
		return base_url + "/wfs"

	def getWcsEndpoint(self, workspace=None, relative=False):
		if relative:
			base_url =  self._get_relative_url(self.frontend_url)
		else:
			base_url = self.frontend_url
		if workspace:
			return base_url + "/" + workspace + "/wcs"
		return base_url + "/wcs"

	def getWmtsEndpoint(self, workspace=None, relative=False):
		if relative:
			base_url =  self._get_relative_url(self.frontend_url)
		else:
			base_url = self.frontend_url
		return base_url + "/gwc/service/wmts"

	def getCacheEndpoint(self, workspace=None, relative=False):
		if relative:
			base_url =  self._get_relative_url(self.frontend_url)
		else:
			base_url = self.frontend_url
		return base_url + "/gwc/service/wms"

	def getGWCRestEndpoint(self, workspace=None, relative=False):
		if relative:
			base_url =  self._get_relative_url(self.frontend_url)
		else:
			base_url = self.frontend_url
		return base_url + "/gwc/rest"

	def __str__(self):
		return self.title_name

	@property
	def title_name(self):
		return "{title} [{name}]".format(title=self.title, name=self.name)

def get_default_server():
    theServer = Server.objects.get(default=True)
    return theServer.id

class Workspace(models.Model):
	server = models.ForeignKey(Server, default=get_default_server, on_delete=models.CASCADE,related_name="WorkspaceServer")
	name = models.CharField(max_length=250, unique=True)
	description = models.CharField(max_length=500, null=True, blank=True)
	uri = models.CharField(max_length=500)
	wms_endpoint = models.CharField(max_length=500, null=True, blank=True)
	wfs_endpoint = models.CharField(max_length=500, null=True, blank=True)
	wcs_endpoint = models.CharField(max_length=500, null=True, blank=True)
	wmts_endpoint = models.CharField(max_length=500, null=True, blank=True)
	cache_endpoint = models.CharField(max_length=500, null=True, blank=True)
	created_by = models.CharField(max_length=100)
	is_public = models.BooleanField(default=False)
	is_delete=models.BooleanField(default=False)
	timestamp=models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name



class Datastore(models.Model):
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
	type = models.CharField(max_length=250)
	name = models.CharField(max_length=250)
	description = models.CharField(max_length=500, null=True, blank=True)
	connection_params = models.JSONField()
	created_by = models.CharField(max_length=100)

	def __str__(self):
		return self.workspace.name + ":" + self.name

	def get_db_connection(self):
		params = json.loads(self.connection_params)
		host = params['host']
		port = params['port']
		dbname = params['database']
		user = params['user']
		passwd = params['passwd']
		i = Introspect(database=dbname, host=host, port=port, user=user, password=passwd)
		return i, params


class LayerGroup(models.Model):
	server_id = models.IntegerField(null=True, default=get_default_server)
	name = models.CharField(max_length=150) 
	title = models.CharField(max_length=500, null=True, blank=True) 
	visible = models.BooleanField(default=False)
	cached = models.BooleanField(default=False)
	created_by = models.CharField(max_length=100)

	def __str__(self):
		return self.name

	def clone(self,recursive=True,target_datastore=None,copy_layer_data=True,permissions=CLONE_PERMISSION_CLONE):
		old_id=self.pk
		new_name=target_datastore.workspace.name + "_" + self.name
		i=1
		salt=''
		while LayerGroup.objects.filter(name=new_name,server_id=target_datastore.workspace.server.id).exists():
			new_name=new_name + "_" + str(i) + salt
			i += 1
			if (i%1000)==0:
				salt="_"+get_random_string(3)
		self.pk=None
		self.name=new_name
		self.save()

		new_instance=LayerGroup.objects.get(pk=self.pk)

		# if recursive:
		# 	for lyr in LayerGroup.objects.get(pk=old_id).layer_set.all():
		# 		lyr.clone(target_datastore=target_datastore,layer_group=new_instance,copy_data=copy_layer_data,permissions=permissions)
		return new_instance


class Layer(models.Model):
    external = models.BooleanField(default=False)
    external_params = models.TextField(null=True, blank=True)
    datastore = models.ForeignKey(Datastore, null=True, on_delete=models.CASCADE)
    layer_group = models.ForeignKey(LayerGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    abstract = models.CharField(max_length=5000, null=True, blank=True)
    type = models.CharField(max_length=150)
    public = models.BooleanField(default=False) # the layer can be read by anyone, even anonymous users
    visible = models.BooleanField(default=True)
    queryable = models.BooleanField(default=True)
    cached = models.BooleanField(default=False)
    single_image = models.BooleanField(default=False)
    vector_tile = models.BooleanField(default=False)
    allow_download = models.BooleanField(default=True)
    order = models.IntegerField(default=100)
    created_by = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='thumbnails', null=True, blank=True)
    # conf = models.TextField(null=True, blank=True)
    timeout = models.IntegerField(null=True, default=30000)
    native_srs = models.CharField(max_length=100, default='EPSG:4326')
    native_extent = models.CharField(max_length=250, default='-180,-90,180,90')
    latlong_extent = models.CharField(max_length=250, default='-180,-90,180,90')
    source_name = models.TextField(null=True, blank=True) # table name for postgis layers, not defined for the rest
    
    def __str__(self):
        return self.name
    
    def get_qualified_name(self):
        return self.datastore.workspace.name + ":" + self.name
    
    def clone(self, target_datastore, recursive=True, layer_group=None, copy_data=True, permissions=CLONE_PERMISSION_CLONE):
        # from gvsigol_services.utils import clone_layer
        # return clone_layer(target_datastore, self, layer_group, copy_data=copy_data, permissions=permissions)
        obj=Layer.objects.get(pk=self.pk)
        self.pk=None
        obj.save()
    
    # def get_config_manager(self):
    #     return LayerConfig(self)

    def get_db_connection(self):
        i, params = self.datastore.get_db_connection()
        return i, self.source_name, params.get('schema', 'public')

