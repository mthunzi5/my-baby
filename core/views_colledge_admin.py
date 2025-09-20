from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge import ColledgeClass
from core.views import is_admin_or_superuser

@user_passes_test(is_admin_or_superuser)
def admin_colledge_list(request):
    classes = ColledgeClass.objects.all().order_by('-created_at')
    if request.method == 'POST':
        class_id = request.POST.get('activate_id')
        if class_id:
            colledge = get_object_or_404(ColledgeClass, id=class_id)
            if not colledge.is_active:
                from django.utils import timezone
                colledge.is_active = True
                colledge.expires_at = timezone.now() + timezone.timedelta(days=30)
                colledge.save()
                messages.success(request, f"Class '{colledge.name}' activated by admin.")
                return redirect('admin_colledge_list')
    return render(request, 'colledge/admin_colledge_list.html', {'classes': classes})

@login_required
def delete_colledge_class(request, colledge_id):
    colledge = get_object_or_404(ColledgeClass, id=colledge_id, owner=request.user)
    if colledge.is_active:
        return redirect('colledge_dashboard', colledge_id=colledge.id)
    if request.method == 'POST':
        colledge.delete()
        messages.success(request, 'Class deleted.')
        return redirect('my_colledge_classes')
    return render(request, 'colledge/confirm_delete_colledge.html', {'colledge': colledge})
