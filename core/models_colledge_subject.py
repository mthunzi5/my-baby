from django.db import models
from .models_colledge import ColledgeClass
from django.conf import settings

class ColledgeSubject(models.Model):
    colledge_class = models.ForeignKey(ColledgeClass, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.colledge_class.name})"
