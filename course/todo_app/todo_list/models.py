from django.db import models

class todo_list(models.Model):
    task = models.CharField(max_length=100)
    details = models.CharField(max_length=150,blank=True)
    status = models.BooleanField(default=False)
    # STATUS_CHOICES = [('C','Complete'),('I','Incomplete')]
    # status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task