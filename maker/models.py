from django.db import models

class ConferenceModule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to="uploads/modules")
    image = models.ImageField(upload_to="uploads/images")
    duration_minutes = models.PositiveIntegerField()

    def __unicode__(self):
        return self.title; 
