from django import forms
from django.forms import ModelForm
from .models import ListEntry

class ListEntryForm(ModelForm):
    class Meta:
        model = ListEntry
        fields = ('rating', 'date_watched', 'comments')
        widgets = {
            'comments': forms.TextInput(attrs={'class':'form-control'})
        }


class UpdateEntryForm(ModelForm):
    class Meta:
        model = ListEntry
        fields = ('rating', 'date_watched', 'comments')
        widgets = {
            'comments': forms.TextInput(attrs={'class':'form-control'})
        }
