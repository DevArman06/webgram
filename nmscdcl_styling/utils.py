from .models import LayerStyle,Style
import re

def encode_xml(sld):
	encoding=get_declared_xml_encoding(sld)
	try:
		return sld.encode(encoding)
	except LookupError:
		return sld.encode("utf-8")

def get_declared_xml_encoding(xml_string):
	"""
    Fast way to get the declared encoding of an XML string. If no
    encoding is declared, utf-8 is assumed.
    xml_string: must be an string, not bytes. 
    """
	pattern=r'^<\?xml(?: *version="[0-9\.]+")? +encoding="([^"]*)"'
	m=re.match(pattern,xml_string)
	if m and m.lastindex==1:
		return m.group(1)
	return 'utf-8'


def has_default_style(layer,style=None):
	layer_styles=LayerStyle.objects.filter(layer=layer)
	for lyr_style in layer_styles:
		print(lyr_style)
		print(lyr_style.style.is_default)
		if style:
			if lyr_style.style.is_default and lyr_style.style.id==style.id:
				return True
		elif lyr_style.style.is_default:
			return True
	return False


def set_not_default_styles(layer):
	layer_styles=LayerStyle.objects.filter(layer=layer)
	for lyr_style in layer_styles:
		st=Style.objects.get(pk=lyr_style.style.id)
		st.is_default=False
		st.save()


def set_default_style(layer,gs,style=None,is_preview=False,is_default=False):
	if is_preview:
		is_default=False
	else:
		if is_default:
			set_not_default_styles(layer)
		elif not has_default_style(layer):
			default=True

		if is_default and style:
			gs.setLayerStyle(layer,style.name,style.is_default)
	return is_default