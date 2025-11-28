from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Contributor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Plant(models.Model):
    scientific_name = models.CharField(max_length=255)
    common_names = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    contributor = models.ForeignKey(Contributor, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.scientific_name

class Phytochemical(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='phytochemicals')
    compound_name = models.CharField(max_length=255)
    compound_class = models.CharField(max_length=255, blank=True)
    biological_activity = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.compound_name

class ScientificLiterature(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='literature')
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    journal = models.CharField(max_length=255)
    doi = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
