from django.db import models

class Tweet(models.Model):
    text = models.CharField(max_length=200)
    time = models.DateTimeField('time')
    user = models.CharField(max_length=20)

    def __unicode__(self):
        return self.text

