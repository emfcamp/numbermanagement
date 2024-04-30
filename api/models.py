from django.db import models
from numman.models import TypeOfService

# Create your models here.
class APIAuth(models.Model):
    label = models.CharField( max_length=50)
    token = models.CharField( max_length=24)
    scope = models.ManyToManyField(TypeOfService)

    def __str__(self):
        return self.label