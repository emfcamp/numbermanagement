from django.db import models
from numman.models import Number, User, Event

# Create your models here.
class Group(models.Model):
    value = models.ForeignKey(Number, on_delete=models.CASCADE, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)    

    def __str__(self):
        return str(self.value_id)

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(Number, on_delete=models.CASCADE)
    delay = models.PositiveIntegerField()

    def __str__(self):
        return str(self.group_id)+"/"+str(self.member_id)