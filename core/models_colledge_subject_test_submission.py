from django.db import models
from .models_colledge_subject_test import ColledgeSubjectTest
from django.conf import settings

class ColledgeSubjectTestQuestion(models.Model):
    test = models.ForeignKey(ColledgeSubjectTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question_text[:40]}..."

class ColledgeSubjectTestSubmission(models.Model):
    test = models.ForeignKey(ColledgeSubjectTest, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.test.name}"

class ColledgeSubjectTestAnswer(models.Model):
    submission = models.ForeignKey(ColledgeSubjectTestSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ColledgeSubjectTestQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"A: {self.answer_text[:40]}..."
