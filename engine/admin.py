from django.contrib import admin
from .models import RunningProcess, Results

class ResultsAdmin(admin.ModelAdmin):

    def get_id(self, obj):
        return '%s' % obj.task_id.task_id
    get_id.short_description = 'Task_id'
        
    list_display = ('process_name', 'get_id', 'filetype', 'get_submitted',)
    list_filter = ('task_id__submited',)
    
admin.site.register(RunningProcess)
admin.site.register(Results, ResultsAdmin)
