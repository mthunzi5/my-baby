from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models_colledge import ColledgeClass

# PayFast config (replace with your merchant_id, merchant_key, return/cancel URLs)
PAYFAST_MERCHANT_ID = '10000100'
PAYFAST_MERCHANT_KEY = '46f0cd694581a'
PAYFAST_PASSPHRASE = ''  # Optional, set if you use passphrase
PAYFAST_URL = 'https://sandbox.payfast.co.za/eng/process'

PLAN_PRICES = {
    500: 200,
    1000: 400,
    2000: 600,
}

@login_required
def payfast_payment(request, colledge_id):
    colledge = get_object_or_404(ColledgeClass, id=colledge_id, owner=request.user)
    amount = PLAN_PRICES.get(colledge.max_members, 200)
    # Build PayFast form data
    payfast_data = {
        'merchant_id': PAYFAST_MERCHANT_ID,
        'merchant_key': PAYFAST_MERCHANT_KEY,
        'return_url': request.build_absolute_uri(f'/colledge/{colledge.id}/payment/success/'),
        'cancel_url': request.build_absolute_uri(f'/colledge/{colledge.id}/payment/cancel/'),
        'notify_url': request.build_absolute_uri(f'/colledge/{colledge.id}/payment/notify/'),
        'name_first': request.user.first_name,
        'name_last': request.user.last_name,
        'email_address': request.user.email,
        'm_payment_id': str(colledge.id),
        'amount': f'{amount:.2f}',
        'item_name': f'Colledge Class: {colledge.name}',
        'item_description': colledge.description,
        'subscription_type': 1,  # recurring
        'recurring_amount': f'{amount:.2f}',
        'frequency': 3,  # monthly
        'cycles': 0,  # 0 = indefinite
    }
    return render(request, 'colledge/payfast_payment.html', {'colledge': colledge, 'payfast_data': payfast_data, 'payfast_url': PAYFAST_URL})
