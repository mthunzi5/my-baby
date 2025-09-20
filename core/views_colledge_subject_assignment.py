from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject import ColledgeSubject
from .models_colledge_subject_assignment import ColledgeSubjectAssignment
from .models_colledge import ColledgeMembership
from .forms_colledge_subject_assignment import ColledgeSubjectAssignmentForm

@login_required
def colledge_subject_assignments(request, subject_id):
    subject = get_object_or_404(ColledgeSubject, id=subject_id)
    colledge = subject.colledge_class
    is_manager = (colledge.owner == request.user)
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or is_manager
    if not is_member:
        return redirect('dashboard')
    assignments = ColledgeSubjectAssignment.objects.filter(subject=subject)
    if request.method == 'POST' and is_manager:
        form = ColledgeSubjectAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.subject = subject
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created.')
            return redirect('colledge_subject_assignments', subject_id=subject.id)
    else:
        form = ColledgeSubjectAssignmentForm()
    return render(request, 'colledge/colledge_subject_assignments.html', {
        'subject': subject,
        'colledge': colledge,
        'assignments': assignments,
        'form': form,
        'is_manager': is_manager,
    })
