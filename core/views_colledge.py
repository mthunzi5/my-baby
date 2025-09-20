from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models_colledge import ColledgeClass
from .forms_colledge import ColledgeClassForm

@login_required
def create_colledge_class(request):
    if request.method == 'POST':
        form = ColledgeClassForm(request.POST)
        if form.is_valid():
            colledge = form.save(commit=False)
            colledge.owner = request.user
            colledge.is_active = False  # Only active after payment
            colledge.save()
            # Redirect to payment page (PayFast integration to be added)
            return redirect('payfast_payment', colledge_id=colledge.id)
    else:
        form = ColledgeClassForm()
    return render(request, 'colledge/create_colledge.html', {'form': form})
