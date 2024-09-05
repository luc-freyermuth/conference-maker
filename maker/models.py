from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class TagCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TagCategory, on_delete=models.RESTRICT)
    
    def __str__(self):
        return self.name

class ConferenceModule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to="uploads/modules")
    image = models.ImageField(upload_to="uploads/images")
    duration_minutes = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, through="ConferenceModuleTag")

    def __str__(self):
        return self.title

class ConferenceModuleTag(models.Model):
    conference_module = models.ForeignKey(ConferenceModule, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    tag_category_importance = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['conference_module', 'tag'], name='unique_module_tag'
            )
        ]