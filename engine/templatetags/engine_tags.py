# -*- encoding: utf-8 -*-
__author__ = 'ernesto (arbitrio@fbk.eu)'
from django import template
from django.conf import settings
from django.core import urlresolvers

register = template.Library()

# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.simple_tag(takes_context=True)
def current(context, url_name, return_value=' active', **kwargs):
    matches = current_url_equals(context, url_name, **kwargs)
    return return_value if matches else ''

@register.filter
def match_url (value):
    return_value = '' 
    if value == 'Network inference':
        return_value = 'network_inference_4'
    
    if value == 'Network stability':
        return_value = 'network_stability_4'

    if value == 'Network distance':
        return_value = 'network_distance_4'
        
    return return_value
        
def current_url_equals(context, url_name, **kwargs):
    resolved = False
    try:
        resolved = urlresolvers.resolve(context.get('request').path)
    except:
        pass
    matches = resolved and resolved.url_name == url_name
    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False
    return matches
