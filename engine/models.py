from django.db import models
import jsonfield
import djcelery

# Create your models here.
class RunningProcess(models.Model):
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
            print res
        else:
            res = None
        return res

    # Returns the time when the task has finished
    @property
    def execution_time(self):
        return self.startered - self.finished  # tmp
