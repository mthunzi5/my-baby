from django.db import models
from .models_colledge_subject_assignment import ColledgeSubjectAssignment
from django.conf import settings

class ColledgeSubjectAssignmentSubmission(models.Model):
    assignment = models.ForeignKey(ColledgeSubjectAssignment, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='colledge_assignment_submissions/')
    grade = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.assignment.title}"
