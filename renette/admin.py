__author__ = 'ernesto'

from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from django.contrib import admin
from redactor.widgets import RedactorEditor
from django.contrib.flatpages.models import FlatPage
from django import forms
from django.utils.translation import ugettext_lazy as _


class FlatPageAdminForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        widgets = {
           'content': RedactorEditor(),
        }


class FlatPageAdmin(admin.ModelAdmin):
    form = FlatPageAdminForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)