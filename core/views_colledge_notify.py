from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models_colledge import ColledgeClass

@csrf_exempt
def payfast_notify(request, colledge_id):
    # In production, validate PayFast signature and payment status!
    if request.method == 'POST':
        # Example: Activate class for 1 month
        colledge = get_object_or_404(ColledgeClass, id=colledge_id)
        colledge.is_active = True
        colledge.expires_at = timezone.now() + timezone.timedelta(days=30)
        colledge.save()
        return HttpResponse('Payment processed', status=200)
    return HttpResponse('Invalid', status=400)

def payfast_success(request, colledge_id):
    return redirect('colledge_dashboard', colledge_id=colledge_id)

def payfast_cancel(request, colledge_id):
    return redirect('colledge_dashboard', colledge_id=colledge_id)
