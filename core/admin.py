from django.contrib import admin

from .models import UserProfile
from .models_site_logo import SiteLogo

admin.site.register(SiteLogo)

admin.site.register(UserProfile)