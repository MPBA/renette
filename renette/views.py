# -*- encoding: utf-8 -*-
import socket

__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm

#from celery.task.control import inspect
import djcelery



class MainView(TemplateView):
    template_name = 'renette/home.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data()

        try:
            c = djcelery.celery
            i = c.control.inspect()
            context['active_processes'] = len(i.active().items()[0][1])
            context['registered_processes'] = len(i.registered().items()[0][1])
            context['scheduled_processes'] = len(i.scheduled().items()[0][1])
        except Exception:
            context['active_processes'] = 'NA'
            context['registered_processes'] = 'NA'
            context['scheduled_processes'] = 'NA'
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


def test_db(request):
    try:
        sites = Site.objects.all()
    except Exception:
        return HttpResponseServerError()
    return HttpResponse('200 OK')


def test_rabbitmq(request):
    try:
        s = socket.socket()
        s.connect_ex(('geopg.fbk.eu', 50010))
    except Exception:
        return HttpResponseServerError()
    return HttpResponse('200 OK')


def test_celery(request):
    try:
         c = djcelery.celery
         i = c.control.inspect()
    except Exception:
        return HttpResponseServerError()
    return HttpResponse('200 OK')
