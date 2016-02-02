from django import template
from django.template.defaultfilters import stringfilter

from core.models import Galaxy, Pair

register = template.Library()

@register.filter(name='url_string_after')
def url_string(lim, view_type):	
	return view_type + '_' + str(lim)
	
@register.filter(name='url_string_before')
def url_string_before(lim, view_type):	
	lim = lim - 100
	if lim == 0:
		return view_type
	return view_type + '_' + str(lim-100)
	
@register.filter(name='url_string')
def url_string(lim, view_type):	
	if view_type.split('_')[0] == 'galaxies':
		galaxies = Galaxy.objects.all().count()
		lim = (int(galaxies/100) * 100) - 100
	else:
		pairs = Pair.objects.all().count()
		lim = (int(pairs/100) * 100) - 100
	return view_type + '_' + str(lim)

@register.filter(name='coordinates')
def pair_coordinates(pair):
	ra = (pair.obj_one.ra + pair.obj_two.ra)/2
	dec = (pair.obj_one.dec + pair.obj_two.dec)/2
	return 'ra=' + str(ra) + '&dec=' + str(dec)
	
type_dict = {'pairs': Pair, 'galaxies': Galaxy}
@register.filter(name='total')
def total(type):
	return type_dict[type].objects.all().count()