from django import forms
from django.core.exceptions import ValidationError
import re

class SearchForm(forms.Form):
    dept = forms.CharField(required = False, widget = forms.TextInput(attrs = {
        'class': 'form-control mb-3',
        'id': 'dept',
        'list': 'dept-list',
        'readonly': True,
        'value': 'CMPSC'
    }))
    cnum = forms.CharField(required = False, widget = forms.TextInput(attrs = {
        'class': 'form-control mb-3',
        'id': 'cnum',
        'list': 'cnum-list',
        'placeholder': 'All'
    }))
    instr = forms.CharField(required = False, widget = forms.TextInput(attrs = {
        'class': 'form-control mb-3',
        'id': 'instr',
        'list': 'instr-list',
        'placeholder': 'All'
    }))
    qtr = forms.CharField(required = False, widget = forms.TextInput(attrs = {
        'class': 'form-control mb-3',
        'id': 'qtr',
        'list': 'qtr-list',
        'placeholder': 'All'
    }))

    def clean(self):
        for v in self.cleaned_data.values():
            if not re.match('^[A-Za-z0-9\s]*$', v):
                raise ValidationError('"{}" is invalid!'.format(v), code='invalid')
