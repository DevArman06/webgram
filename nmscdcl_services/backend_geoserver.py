from .backend_postgis import Introspect
import gdaltools
import logging
from dbfread import DBF
from nmscdcl import settings
from nmscdcl.settings import CONTROL_FIELDS
import re
from .backend_postgis import Introspect
import json
import os
# from django.conf import api_settings
from pathlib import Path
from nmscdcl import settings
from osgeo import osr
import geoserver.catalog as gscat
from django.utils.translation import gettext_lazy as _
from . import rest_geoserver
from nmscdcl_styling.models import LayerStyle,Style
from .rest_geoserver import RequestError


logger = logging.getLogger("nmscdcl")
_valid_sql_name_regex=re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")

supported_crs_array=[]
for item in list(settings.SUPPORTED_CRS.items()):
                supported_crs_array.append(item[1])

supported_encodings = tuple((x,x) for x in settings.SUPPORTED_ENCODINGS)
supported_encodings = supported_encodings + (('autodetect', 'autodetect'),)
supported_srs = tuple((x['code'],x['code']+' - '+x['title']) for x in supported_crs_array)

supported_srs_plain = [ x[0] for x in supported_srs ]
supported_encodings_plain = [ x[0] for x in supported_encodings ]


class Geoserver(): #need to fixed

    def __init__(self,id,default,name,user,password,master_node):
        self.id = id
        self.default = default
        self.name = name
        self.conf_url = master_node
        self.rest_url = master_node + "/rest"
        self.gwc_url = master_node + "/gwc/rest"
        # self.slave_node = slave_node
        self.rest_catalog = rest_geoserver.Geoserver(self.rest_url, self.gwc_url)
        self.user = user
        self.password=password
        self.supported_types = (
            ('v_PostGIS', _('PostGIS vector')),
            ('c_GeoTIFF', _('GeoTiff')),
            ('e_WMS', _('Cascading WMS')),
            ('c_ImageMosaic', _('ImageMosaic')),
        )

    def getGsconfig(self):
        return gscat.Catalog(self.rest_url, self.user, self.password, validate_ssl_certificate=False)

    def reload_node(self, node_url):
        try:
            self.rest_catalog.reload(node_url, user=self.user, password=self.password) 
            return True
        
        except Exception as e:
            print(str(e))
            return False


    def getGsLayers(self):
        catalog=self.getGsconfig()
        # resource=catalog.get_resources(workspaces="tiger")
        layer_data=catalog.get_layers()
        return layer_data

    def getGsLayer(self,layer_name):
        catalog=self.getGsconfig()
        layer_data=catalog.get_layer(name=layer_name)
        return layer_data

    def setLayerStyle(self,layer,style,is_default):
        """
        Set default style
        """
        try:
            layer_name=layer.get_qualified_name()
            print(layer_name)
            catalog=self.getGsconfig()
            gs_layer=catalog.get_layer(layer_name)
            print(" i am adding the style")
            self.addStyle(layer,layer_name,style)
            print("i am after add style")
            if is_default:
                gs_layer.default_style=style
            print(gs_layer,"before catalog.save")
            catalog.save(gs_layer)
            return True

        except Exception as e:
            print(e)
            print("issue in set layer style")
            return False

    def createOverwrittenStyle(self, name, data, overwrite):

        """
        Create new style or overwrite an existing file
        """

        try:
            self.getGsconfig().create_style(name, data, overwrite=overwrite, workspace=None, style_format="sld10", raw=False)
            return True
        except Exception as e:
            print("Got error %s while creating style"%(e))
            return False

    def create_style(self,name,data):
        return self.createOverwrittenStyle(name,data,False)


    def addStyle(self,layer,layer_name,name):
        self.rest_catalog.add_style(layer_name,name,user=self.user,password=self.password)

        if layer is not None:
            style_list=[]
            default_style=""
            layer_styles=LayerStyle.objects.filter(layer=layer)
            for layer_style in layer_styles:
                if not layer_style.style.name.endswith("_tmp"):
                    style_list.append(layer_style.style.name)
                if layer_style.style.is_default:
                    default_style=layer_style.style.name
            self.rest_catalog.update_layer_style_configuration(layer_name,name,default_style,style_list,user=self.user,password=self.password)

    def updateStyle(self,layer,style_name,sld_body):
        try:
            self.rest_catalog.update_style(style_name,sld_body,user=self.user,password=self.password)

            layer_name=layer.get_qualified_name()
            if layer is not None:
                style_list=[]
                default_style=""
                layer_styles=LayerStyle.objects.filter(layer=layer)
                for layer_style in layer_styles:
                    if not layer_style.style.name.endswith("_tmp"):
                        style_list.append(layer_style.style.name)
                    if layer_style.style.is_default:
                        default_style=layer_style.style.name
                self.rest_catalog.update_layer_style_configuration(layer_name,style_name,default_style,style_list,user=self.user,password=self.password)
            return True
        except RequestError as e:
            print("error in updating style ",style_name)
            print(e.get_detailed_message())
        except Exception:
            print("error in updating style ",style_name)
            return False

        


def __fieldmapping_sql(creation_mode, shp_path, shp_fields, table_name, host, port, db, schema, user, password):
    if creation_mode == "CREATE":
        # no mapping needed
        return
    
    i = Introspect(db, host=host, port=port, user=user, password=password)
    db_fields = i.get_fields(table_name, schema=schema)
    db_pks = i.get_pk_columns(table_name, schema=schema)
    i.close()
    if len(db_pks) == 1:
        db_pk = db_pks[0]
    else:
        db_pk = 'ogc_fid'
    
    if 'ogc_fid' in shp_fields:
        # ogr will use this as pk, nothing to do
        pk = 'ogc_fid'
    elif db_pk in shp_fields:
        pk = db_pk
    else:
        pk = None

    fields = []
    pending = []
    for f in shp_fields:
        if f == pk:
            fields.append('"' + f + '" as ogc_fid')
        elif f in db_fields:
            ctrl_field = next((the_f for the_f in CONTROL_FIELDS if the_f.get('name') == f), None)
            if ctrl_field:
                if creation_mode=="APPEND":
                    # skip control field in append mode
                    continue
                elif ctrl_field.get('type', '').startswith('timestamp'):
                    fields.append('CAST("' + f + '" AS timestamp)')
                    continue
            fields.append('"' + f + '"')
        else:
            pending.append(f)
    
    if (pk is None or pk == 'ogc_fid') and len(pending) == 0:
        # no mapping needed
        return
    for f in pending:
        # try to find a mapping
        db_mapped_field = None
        for db_field in db_fields:
            if db_field.startswith(f):
                db_mapped_field = db_field
        if not db_mapped_field:
            for db_field in db_fields:
                if db_field.startswith(f.rstrip('0123456789')):
                    # remove numbers in the right side of the field name to try to match with db
                    db_mapped_field = db_field
        if db_mapped_field:
            ctrl_field = next((the_f for the_f in CONTROL_FIELDS if the_f.get('name') == db_mapped_field), None)
            if ctrl_field:
                if creation_mode=="APPEND":
                    # skip control field in append mode
                    continue
                elif ctrl_field.get('type', '').startswith('timestamp'):
                    fields.append('CAST("' + f + '" AS timestamp) as "' + db_mapped_field + '"')
                    db_fields.remove(db_mapped_field)
                    continue
            fields.append('"' + f + '" as "' + db_mapped_field + '"')
            db_fields.remove(db_mapped_field)
        else:
            fields.append('"' + f + '"')
    
    shp_name = os.path.splitext(os.path.basename(shp_path))[0]
    sql = "SELECT " + ",".join(fields) + " FROM " + shp_name
    return sql
    
def shp2postgis(shp_path, table_name, srs, host, port, dbname, schema, user, password, creation_mode="CREATE", encoding="autodetect", sql=None):
    ogr = gdaltools.ogr2ogr()
    ogr.set_encoding(encoding)
    print(shp_path)
    ogr.set_input(shp_path, srs=srs)
    conn = gdaltools.PgConnectionString(host=host, port=port, dbname=dbname, schema=schema, user=user, password=password)
    ogr.set_output(conn, table_name=table_name)
    if creation_mode == "CREATE":
        ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_CREATE, data_source_mode=ogr.MODE_DS_UPDATE)
    elif creation_mode == "APPEND":
            ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_APPEND, data_source_mode=ogr.MODE_DS_UPDATE)
    elif creation_mode == "OVERWRITE":
            ogr.set_output_mode(layer_mode=ogr.MODE_LAYER_OVERWRITE, data_source_mode=ogr.MODE_DS_UPDATE)
    ogr.layer_creation_options = {
        "LAUNDER": "YES",
        "precision": "NO"
    }
    ogr.config_options = {
        "OGR_TRUNCATE": "NO"
    }
    ogr.set_sql(sql)
    ogr.set_dim("2")
    ogr.geom_type = "PROMOTE_TO_MULTI"
    print("shp2postgis")
    print(shp_path)
    ogr.execute()
    print(" ".join(ogr.safe_args))
    return ogr.stderr if ogr.stderr is not None else ''

def __do_export_to_postgis(name, connection_params, form_data, shp_path, shp_fields):
    try:
        name = name.lower()
        # get & sanitize parameters
        srs = form_data.get('srs')
        encoding = form_data.get('encoding')
        creation_mode = form_data.get('mode')
        if not encoding in supported_encodings_plain or not srs in supported_srs_plain:
            raise rest_geoserver.RequestError()
        # FIXME: sanitize connection parameters too!!!
        # We are going to perform a command line execution with them,
        # so we must be ABSOLUTELY sure that no code injection can be
        # performed
        ds_params = connection_params
        db = ds_params.get('database')
        host = ds_params.get('host')
        port = ds_params.get('port')
        schema = ds_params.get('schema', "public")
        port = str(int(port))
        user = ds_params.get('user')
        password = ds_params.get('passwd')
        if _valid_sql_name_regex.search(name) == None:
            raise InvalidValue(-1, _("Invalid layer name: '{value}'. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=name))
        if _valid_sql_name_regex.search(db) == None:
            raise InvalidValue(-1, _("The connection parameters contain an invalid database name: {value}. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=db))
        if _valid_sql_name_regex.search(user) == None:
            raise InvalidValue(-1, _("The connection parameters contain an invalid user name: {value}. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=db))
        if _valid_sql_name_regex.search(schema) == None:
            raise InvalidValue(-1, _("The connection parameters contain an invalid schema: {value}. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=db)) 

        shp_field_names = [f.name for f in shp_fields]
        sql = __fieldmapping_sql(creation_mode, shp_path, shp_field_names, name, host, port, db, schema, user, password)
        stderr = shp2postgis(shp_path, name, srs, host, port, db, schema, user, password, creation_mode, encoding, sql)
        if stderr.startswith("ERROR"): # some errors don't return non-0 status so will not directly raise an exception
            raise rest_geoserver.RequestError(-1, stderr)
        with Introspect(db, host=host, port=port, user=user, password=password) as i:
            # add control fields
            db_fields = i.get_fields(name, schema=schema)
            for control_field in settings.CONTROL_FIELDS:
                has_control_field = False
                for field in db_fields:
                    if field == control_field['name']:
                        try:
                            i.set_field_default(schema, name, control_field['name'], control_field.get('default'))
                        except:
                            logger.exception("Error setting default value for control field: " + control_field['name'])
                        has_control_field = True
                if not has_control_field:
                    try:
                        i.add_column(schema, name, control_field['name'], control_field['type'], nullable=control_field.get('nullable', True), default=control_field.get('default'))
                    except:
                        logger.exception("Error adding control field: " + control_field['name'])
            if creation_mode == "OVERWRITE":
                i.update_pk_sequences(name, schema=schema)
        
        if creation_mode == "OVERWRITE":
            # re-install triggers
            for trigger in Trigger.objects.filter(layer__datastore=datastore, layer__source_name=name):
                try:
                    trigger.drop()
                    trigger.install()
                except:
                    logger.exception("Failed to install trigger: " + str(trigger))
            
        # for layer in Layer.objects.filter(datastore=datastore, source_name=name):
        #     self.reload_featuretype(layer)
        #     expose_pks = self.datastore_check_exposed_pks(datastore)
        #     layer.get_config_manager().refresh_field_conf(include_pks=expose_pks)
        #     layer.save()
        # if not stderr:
        #     return True
    except Exception as e:
        logger.exception(str(e))
        raise
    # except gdaltools.GdalToolsError as e:
    #     logger.exception(str(e))
    #     if e.code > 0 and creation_mode == "OVERWRITE":
    #         params = json.loads(connection_params)
    #         host = params['host']
    #         port = params['port']
    #         dbname = params['database']
    #         user = params['user']
    #         passwd = params['passwd']
    #         schema = params.get('schema', 'public')
    #         i = Introspect(database=dbname, host=host, port=port, user=user, password=passwd)
    #         i.delete_table(schema, name)
    #         i.close()
    #         try:
    #             stderr = self.shp2postgis(shp_path, name, srs, host, port, db, schema, user, password, creation_mode, encoding)
    #             if stderr:
    #                 raise rest_geoserver.RequestError(-1, stderr)
    #             return True
    #         except gdaltools.GdalToolsError as e:
    #             raise rest_geoserver.RequestError(e.code, str(e))
    #     raise rest_geoserver.RequestError(e.code, str(e))
    # except Exception as e:
    #     logger.exception(str(e))
    #     message =  _("Error uploading the layer. Review the file format. Cause: ") + str(e)
    #     raise rest_geoserver.RequestError(-1, message)
    # raise rest_geoserver.RequestWarning(stderr)

def get_fields_from_shape(shp_path):
    fields = {}
    fields['fields'] = {}
    
    dbf_file = shp_path.replace('.shp', '.dbf').replace('.SHP', '.dbf')
    print(dbf_file,"this is my dbf")
    if not os.path.isfile(dbf_file):
        print("IT IS NOT A FILE")
        dbf_file = dbf_file.replace('.dbf', '.DBF')
    print("it is a file")
    print(dbf_file)
    table = DBF(dbf_file)
    print(table.fields)                
    return table.fields

def getprj(shp_path):
    prj_file=shp_path.replace('.shp','.prj').replace('.SHP','.prj')
    print(prj_file,"this is my prj file")
    if not os.path.isfile(prj_file):
        prj_file=prj_file.replace('.prj','.PRJ')
    print(prj_file)
    with open("prj_file","r") as f:
        prj_text=f.read()
    srs=osr.SpatialReference()
    srs.ImportFromEPSG([prj_text])
    print("Shape prj is : ",prj_text)
    print("wkt4 is : ",str(srs.ExportToWkt()))
    print("proj4 is : ",str(srs.ExportToProj4()))
    srs.AutoIdentifyEPSG()
    print("EPSG is : ",str(srs.GetAuthorityCode(None)))



def exportShpToPostgis(form_data):
    name = form_data['name']
    ds = form_data['connection_params']
    # shp_path = form_data['file']
    # shp_path=os.path.join(settings.BASE_DIR,shp_path)
    shp_path = "D:\\Projects BGIS\\NMSCDCL\\nmscdcl\\media\\countries\\countries.shp"
    # shp_path=os.path.join(settings.MEDIA_ROOT,"tiger_roads.shp")
    print("backend_geoserver")
    print(shp_path)
    print(settings.BASE_DIR,"this is base dir")
    
    
    fields = get_fields_from_shape(shp_path)
    for field in fields:
        if ' ' in field.name:
            raise InvalidValue(-1, _("Invalid layer fields: '{value}'. Layer can't have fields with whitespaces").format(value=field.name))
        
    
    if _valid_sql_name_regex.search(name) == None:
        raise InvalidValue(-1, _("Invalid layer name: '{value}'. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=name))
                
    try:
        __do_export_to_postgis(name, ds, form_data, shp_path, fields)
        return True

    except Exception as e:
        print(e)
        raise e