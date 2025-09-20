from django.db import models
from django.conf import settings
from django.utils import timezone

class ColledgeClass(models.Model):
    PLAN_CHOICES = [
        (500, 'R200 for 500 people'),
        (1000, 'R400 for 1000 people'),
        (2000, 'R600 for 2000 people'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_colledges')
    is_active = models.BooleanField(default=False)
    max_members = models.PositiveIntegerField(choices=PLAN_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class ColledgeMembership(models.Model):
    colledge_class = models.ForeignKey(ColledgeClass, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='colledge_memberships')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('colledge_class', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.colledge_class.name}"
