from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class SiteLogo(models.Model):
    logo = models.ImageField(
        upload_to='site_logo/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'ico'])]
    )
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Site Logo uploaded at {self.uploaded_at}"
