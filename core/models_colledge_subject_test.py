from django.db import models
from .models_colledge_subject import ColledgeSubject
from django.conf import settings

class ColledgeSubjectTest(models.Model):
    subject = models.ForeignKey(ColledgeSubject, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    open = models.BooleanField(default=False, help_text="If open, students can take the test.")

    def __str__(self):
        return f"{self.name} ({self.subject.name})"
