from django.db import models
from .models_colledge_subject import ColledgeSubject
from django.conf import settings

class ColledgeSubjectFile(models.Model):
    subject = models.ForeignKey(ColledgeSubject, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='colledge_subject_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.file.name} ({self.subject.name})"
