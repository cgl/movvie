from django.db import models

class Movie(models.Model):
    movvie_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    release_date = models.DateField('date released')
    url = models.URLField()
    rating = models.FloatField()

    def __unicode__(self):
        return self.title

class Review(models.Model):
    movie = models.ForeignKey(Movie)
    body = models.TextField()
    date = models.DateTimeField('review date')
    rating = models.FloatField()

    def __unicode__(self):
        return self.body

class Sentence(models.Model):
    SENT_CHOICES = (
    ('P', 'Positive'),
    ('N', 'Negative'),
    ('U', 'Neutral'),
    ('O', 'Bozuk'),
    )
    sentence_id = models.IntegerField(unique=True)
    review = models.ForeignKey(Review)
    body = models.TextField()
    sentiment = models.CharField(max_length=1, choices=SENT_CHOICES)
