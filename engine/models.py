from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import jsonfield
import djcelery
import os

# Create your models here.
from engine.utils import get_bootsrap_badge


class RunningProcess(models.Model):
    #user = models.ForeignKey(User)
    process_name = models.CharField(max_length=40)
    task_id = models.CharField(max_length=36)
    #files = jsonfield.JSONField(blank=True, null=True)
    inputs = jsonfield.JSONField()
    submited = models.DateTimeField()
    startered = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)


    # From id returns task result
    @property
    def celery_task(self):
        try:
            return djcelery.celery.AsyncResult(self.task_id)
        except Exception:
            return None

    @property
    def to_pretty_inputs(self):
        res = []
        for key, value in self.inputs.items():
            if value == None:
                value = 'NA'
            if key == 'header':
                key = 'with_col_header'
            if key == 'row.names':
                key = 'with_row_header'
                value = bool(value)
            tmp = '<li><strong>%s</strong>=%s</li>' % (key, value)
            res.append(tmp)
        return ', '.join(res)

    @property
    def badge_status(self):
        task = self.celery_task
        return '<span class="label %s">%s</span>' % (get_bootsrap_badge(task.status), task.status)

    ## Check if the task has finished
    #@property
    #def finished(self):
    #    return self.celery_task.ready()
    #
    ## Return the current status of the task
    #@property
    #def status(self):
    #    return self.celery_task.status
    #
    ## Returns the result of the task
    @property
    def result(self):
        if self.celery_task.status == 'SUCCESS':
            res = self.celery_task.result
        else:
            res = None
        return res

    @property
    def result_is_sucess(self):
        if self.celery_task.status == 'SUCCESS' and isinstance(self.celery_task.result,dict):
            res = True
        else:
            res = False
        return res

    # Returns the time when the task has finished
    @property
    def execution_time(self):
        return self.startered - self.finished  # tmp

class Results(models.Model):
    
    """
    Results table: need for storing the results instead of pass through celery
    """
    def get_tmp_dir(self, filename):
        return os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH, self.task_id.task_id, filename)
    
    FILE_TYPES = (
        ('csv','comma separated file'),
        ('img', 'jpg, tiff, png, pdf'),
        ('graph', 'gml, graphml'),
        ('txt', 'text description'),
        ('json', 'jsoon file'),
        ('rdata', 'R compressed format, binary'),
        ('error', 'Error during computation')
    )
    
    process_name = models.CharField(max_length=40)
    task_id = models.ForeignKey(RunningProcess)
    #files = jsonfield.JSONField(blank=True, null=True)
    filetype = models.CharField(max_length=36, choices=FILE_TYPES)
    filename = models.CharField(max_length=40)
    filepath = models.CharField(max_length=100)
    filestore = models.FileField(upload_to=get_tmp_dir)
    imagestore = models.ImageField(upload_to=get_tmp_dir)
    desc = models.TextField()
    
    def __unicode__(self):
        return u'%s: %s' % (self.task_id.task_id, self.filetype)
        
    def get_submitted(self):
        return self.task_id.submited
    get_submitted.short_description='Submit time'
