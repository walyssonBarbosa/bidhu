# coding:utf-8
from chartit import DataPool, Chart
from django.core.mail import EmailMessage
from django.db.models import Max, Min
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render, render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.template.loader import get_template
from itertools import combinations
import csv, math, json

from scripts.sqlcl import query
from models import Galaxy, Pair
from forms import ImportDataForm, ContactForm
from conf.settings import EMAIL_HOST_USER

def home(request):
	return render_to_response("index.html")
	
def about(request):	
	return render_to_response("about.html")
	
def contact(request):	
	form_class = ContactForm
	if request.method == 'POST':
		form = form_class(data=request.POST)
		if form.is_valid():
			contact_name = request.POST.get('contact_name', '')
			contact_email = request.POST.get('contact_email', '')
			form_content = request.POST.get('content', '')			
			template = get_template('contact_template.txt')
			context = Context({
				'contact_name': contact_name,
				'contact_email': contact_email,
				'form_content': form_content,})
			content = template.render(context)			
			email = EmailMessage(
				"New message - BIDHU",
				content,				
				to=['project_email'],
				headers = {'Reply-To': contact_email }
			)
			try:
				email.send()
				return render(request, "contact.html", {'message': 'success'}, context_instance=RequestContext(request))
			except:
				return render(request, "contact.html", {'message': 'error'}, context_instance=RequestContext(request))
	return render(request, "contact.html", {'form': form_class, 'message': 'neutral'}, context_instance=RequestContext(request))
	
def calculate_distance(g1, g2):        
	return math.acos(math.sin(math.radians(g1.dec)) * math.sin(math.radians(g2.dec)) + math.cos(math.radians(g1.dec)) * math.cos(math.radians(g2.dec)) * math.cos(math.radians(g2.ra) - math.radians(g1.ra)))
	
def import_data(request):
	galaxies = []
	pairs = []
	if request.method == "POST":
		form = request.POST['options']					
		if 'mode' not in request.POST or request.POST['mode'] != 'on':
			for gs in request.FILES['file'].chunks():
				gs = gs.split("\r\n")
				for g in gs:
					line = g.split(',')
					if len(line) == 3:
						galaxy, created = Galaxy.objects.get_or_create(obj_id=int(line[0]), ra=float(line[1]), dec=float(line[2]))
						if created:
							galaxies.append(galaxy)
		else:
			sql_result = query(request.POST['sql']).read().split('\n')[2:-1]
			for line in sql_result:
				line = line.split(',')
				galaxy, created = Galaxy.objects.get_or_create(obj_id=int(line[0]), ra=float(line[1]), dec=float(line[2]))
				if created:
					galaxies.append(galaxy)
		if form == 'impchec':
			for g in combinations(galaxies, 2):
				distance = calculate_distance(g[0], g[1])
				if distance <= 0.000290888209:					
					pair, created = Pair.objects.get_or_create(obj_one=g[0], obj_two=g[1], distance=distance)
					if created:
						pairs.append(pair)
	else:
		form = ImportDataForm()
	return render(request, "import_data.html", {'galaxies': len(galaxies), 'pairs': len(pairs), 'form': form}, context_instance=RequestContext(request))
	
def check(request):
	galaxies = Galaxy.objects.all()
	if galaxies.count():
		pairs = []
		for g in combinations(galaxies, 2):
					distance = calculate_distance(g[0], g[1])
					if distance <= 0.000290888209:					
						pair, created = Pair.objects.get_or_create(obj_one=g[0], obj_two=g[1], distance=distance)
						if created:
							pairs.append(pair)
		return render_to_response("check.html", {'pairs': len(pairs)})
	return render_to_response("check.html", {'pairs': -1})

def download(request, output_type):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="catalog_{}.csv"'.format(output_type)
	writer = csv.writer(response)
	if output_type == 'pairs':
		pairs = Pair.objects.all()
		if pairs:
			writer.writerow(['obj1', 'ra1', 'dec1', 'obj2', 'ra2', 'dec2', 'separacao'])
			for pair in pairs:
				writer.writerow([str(pair.obj_one.obj_id), str(pair.obj_one.ra), str(pair.obj_one.dec), str(pair.obj_two.obj_id), str(pair.obj_two.ra), str(pair.obj_two.dec), str(pair.distance)])
		else:
			writer.writerow(["No pair present in the database!"])		
	else:
		galaxies = Galaxy.objects.all()
		if galaxies:
			writer.writerow(['objId', 'ra', 'dec'])
			for galaxy in galaxies:
				writer.writerow([str(galaxy.obj_id), str(galaxy.ra), str(galaxy.dec)])
		else:
			writer.writerow(["No galaxy present in the database!"])		
	return response
	
type_dict = {'pairs': [Pair, 0], 'galaxies': [Galaxy, 1]}
def view(request, view_type):
	view_type = view_type.split('_')		
	if len(view_type) > 1:		
		ini = int(view_type[1])
		lim = ini + 100
	else:
		ini = 0
		lim = 100
	objects = type_dict[view_type[0]][0].objects.all()		
	if len(objects) < lim:			
		lim = -1
		objects = objects[ini:]		
	else:
		objects = objects[ini:lim]
	return render_to_response("table.html", {'objects': objects, 'type':  type_dict[view_type[0]][1], 'lim': lim})

def display_galaxy(request, obj_id):
	galaxy = get_object_or_404(Galaxy, obj_id=obj_id)
	return render_to_response("display.html", {'galaxy': galaxy})
	
def display_pair(request, id):
	pair = get_object_or_404(Pair, id=id)
	return render_to_response("display.html", {'pair': pair})
	
def display_chart(request):
	galaxies = Galaxy.objects.all()
	if galaxies.count():
		coord_values = {'ra': {} , 'dec': {}}
		for coord in ['ra', 'dec']:		
			coord_values[coord]['min'] = galaxies.aggregate(Min(coord))[coord+'__min']
			coord_values[coord]['max'] = galaxies.aggregate(Max(coord))[coord+'__max']
		pairs = Pair.objects.all()
		are_pairs = []
		for pair in pairs:
			if pair.obj_one not in are_pairs:
				are_pairs.append(pair.obj_one)
			if pair.obj_two not in are_pairs:
				are_pairs.append(pair.obj_two)	
		all_objects = {
			'galaxies': {
				'obj_id_list': [],
				'ra_list': [],
				'dec_list': []}, 
			'pairs': {
				'obj_id_list': [],
				'ra_list': [],
				'dec_list': []}}			
		for galaxy in galaxies:
			if galaxy not in are_pairs:
				all_objects['galaxies']['obj_id_list'].append(str(galaxy.obj_id))
				all_objects['galaxies']['ra_list'].append(galaxy.ra)
				all_objects['galaxies']['dec_list'].append(galaxy.dec)	
		for galaxy in are_pairs:
			all_objects['pairs']['obj_id_list'].append(str(galaxy.obj_id))
			all_objects['pairs']['ra_list'].append(galaxy.ra)
			all_objects['pairs']['dec_list'].append(galaxy.dec)
		all_objects['galaxies']['obj_id_list'] = json.dumps(all_objects['galaxies']['obj_id_list'])
		all_objects['pairs']['obj_id_list'] = json.dumps(all_objects['pairs']['obj_id_list'])
		return render_to_response('statistics.html',{'all_objects': all_objects, 'coord_values': coord_values})
	return render_to_response('statistics.html',{'all_objects': [], 'coord_values': []})