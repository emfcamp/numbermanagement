from django.db import models
from numman.models import Number, User, Event

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.ForeignKey(Number, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    
    def __str__(self):
        return  str(self.id)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'value'], name='unique_event_group')
        ]

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(Number, on_delete=models.CASCADE)
    delay = models.PositiveIntegerField()
    
    def __str__(self):
        return str(self.group_id) + "/" + str(self.member_id)