from django.db import models
from .models_colledge_subject import ColledgeSubject
from django.conf import settings

class ColledgeSubjectAssignment(models.Model):
    subject = models.ForeignKey(ColledgeSubject, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"
