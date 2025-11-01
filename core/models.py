from django.db import models

# Create your models here.
class Conversation(models.Model):
    title = models.CharField(max_length=200)
    history = models.JSONField(default=list)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


