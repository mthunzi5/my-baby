from .models_site_logo import SiteLogo

def site_logo(request):
    logo = SiteLogo.objects.order_by('-uploaded_at').first()
    return {'site_logo': logo}