from .models import Style,LayerStyle
from nmscdcl_services.models import Layer
from . import utils


def create_style(style_name,style_title,sld,is_default,layer,gs,is_preview=False):
	if is_preview:
		style_name = style_name+"_tmp"
	is_default=utils.set_default_style(layer,gs,is_preview=is_preview,is_default=is_default)

	style=Style(
		name=style_name,
		title=style_title,
		is_default=is_default,
		sld=sld
		)
	style.save()

	layer_style=LayerStyle(
		layer=layer,
		style=style
		)
	layer_style.save()

	sld_body=utils.encode_xml(sld)

	if is_preview:
		if gs.createOverwrittenStyle(style_name,sld_body,True):
			return style
	else:
		if gs.create_style(style_name,sld_body):
			gs.setLayerStyle(layer,style_name,is_default)
			return style
 	