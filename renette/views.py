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
from django.core.mail import send_mail
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
            messages.add_message(request, messages.SUCCESS, 'Message sent successfully! Thanks for your interest!')

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = 'message by <%s> \n%s' % (email, form.cleaned_data['message'])

            #cc_myself = form.cleaned_data['cc_myself']

            recipients = ['droghetti@fbk.eu', 'filosi@fbk.eu']
            try:
                send_mail("RENETTE contact info", message, 'RENETTE DAEMON <%s>' % settings.EMAIL_HOST_USER, recipients)
            except Exception:
                messages.add_message(request, messages.ERROR, 'An error occurred! Check the form field and try again!')

            return HttpResponseRedirect('/contact/')  # Redirect after POST
        else:
            messages.add_message(request, messages.ERROR, 'An error occurred! Check the form field and try again!')
            return HttpResponseRedirect('/contact/')  # Redirect after POST
    else:
        return HttpResponseBadRequest