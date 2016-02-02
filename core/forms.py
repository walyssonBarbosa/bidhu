# coding:utf-8
from django import forms

IMPORT_OPTIONS = (
('imponly', 'Import Only'),
('impchec', 'Import & Check for Pairs')
)
class ImportDataForm(forms.Form):
	file = forms.FileField()
	options = forms.MultipleChoiceField(required=True, widget=forms.RadioSelect, choices=IMPORT_OPTIONS)
	sql = forms.CharField(widget=forms.Textarea)
	mode = forms.BooleanField()

class ContactForm(forms.Form):
	contact_name = forms.CharField(label='Name', required=True)
	contact_email = forms.EmailField(label='Email', required=True)
	content = forms.CharField(
		label='Message',
		required=True,
		widget=forms.Textarea
	)