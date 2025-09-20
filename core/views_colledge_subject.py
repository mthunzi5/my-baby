from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge import ColledgeClass, ColledgeMembership
from .models_colledge_subject import ColledgeSubject
from .forms_colledge_subject import ColledgeSubjectForm

@login_required
def colledge_subjects(request, colledge_id):
    colledge = get_object_or_404(ColledgeClass, id=colledge_id)
    # Only owner/manager can add subjects
    is_manager = (colledge.owner == request.user)
    # Members can view
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or is_manager
    if not is_member:
        return redirect('dashboard')
    subjects = ColledgeSubject.objects.filter(colledge_class=colledge)
    if is_manager and request.method == 'POST':
        form = ColledgeSubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.colledge_class = colledge
            subject.created_by = request.user
            subject.save()
            messages.success(request, 'Subject created.')
            return redirect('colledge_subjects', colledge_id=colledge.id)
    else:
        form = ColledgeSubjectForm()
    return render(request, 'colledge/colledge_subjects.html', {
        'colledge': colledge,
        'subjects': subjects,
        'form': form,
        'is_manager': is_manager,
    })
