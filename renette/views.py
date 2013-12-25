# -*- encoding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt

__author__ = 'ernesto'

#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from .forms import ContactForm
import random

#class based view for home page rendering
class MainView(TemplateView):
    template_name = 'renette/home.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data()
        return context


@csrf_exempt
def contact(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            messages.add_message(request, messages.SUCCESS, 'email ok')

            name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            #cc_myself = form.cleaned_data['cc_myself']

            recipients = ['droghetti@fbk.eu', 'filosi@fbk.eu']

            from django.core.mail import send_mail
            send_mail("RENETTE contact info", message, 'RENETTE DAEMON <%s>' % settings.EMAIL_HOST_USER, recipients)

            return HttpResponseRedirect('/contact/')  # Redirect after POST
        else:
            messages.add_message(request, messages.ERROR, 'email ko')
            return HttpResponseRedirect('/contact/')  # Redirect after POST
    else:
        #form = ContactForm()  # An unbound form
        #messages.add_message(request, messages.ERROR, '')
        return HttpResponseBadRequest