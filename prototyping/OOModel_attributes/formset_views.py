from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render
from django.forms.models import formset_factory, inlineformset_factory, modelformset_factory, modelform_factory
from django import forms

import traceback
import wdb

class CustomForm(forms.Form):
    title = forms.CharField()

    def clean(self):
        raise forms.ValidationError("FORM level error.")


class CustomFormset(forms.BaseFormSet):
    def clean(self):
        raise forms.ValidationError("FORMSET level error.")

def formset_error(request):
    FormSetClass = formset_factory(CustomForm, formset=CustomFormset, extra=2)
    formset = FormSetClass()
    if formset.is_valid():
        pass
    return HttpResponse("formset_error() view function completed.")

def formset_error_bkp(request):
    #wdb.set_trace()
    FormSetClass = formset_factory(CustomForm, formset=CustomFormset, extra=2)
    if request.method == 'POST':
        print(request.POST)
        formset = FormSetClass(request.POST)
        if formset.is_valid():
            pass
    else:
        formset = FormSetClass()
    return render(request, "OOModel/form.html", { 'formset': formset })
