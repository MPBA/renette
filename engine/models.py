from django.db import models
from django.contrib.auth.models import User
import jsonfield
import djcelery


# Create your models here.
from engine.utils import get_bootsrap_badge


class RunningProcess(models.Model):
    #user = models.ForeignKey(User)
    process_name = models.CharField(max_length=40)
    task_id = models.CharField(max_length=36)
    inputs = jsonfield.JSONField()
    submited = models.DateTimeField()
    startered = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)


    # From id returns task result
    @property
    def celery_task(self):
        return djcelery.celery.AsyncResult(self.task_id)

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
