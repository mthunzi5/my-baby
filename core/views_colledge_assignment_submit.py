from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject_assignment import ColledgeSubjectAssignment
from .models_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmission
from .forms_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmissionForm
from .models_colledge import ColledgeMembership

@login_required
def colledge_assignment_submit(request, assignment_id):
    assignment = get_object_or_404(ColledgeSubjectAssignment, id=assignment_id)
    colledge = assignment.subject.colledge_class
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or (colledge.owner == request.user)
    if not is_member:
        return redirect('dashboard')
    already_submitted = ColledgeSubjectAssignmentSubmission.objects.filter(assignment=assignment, user=request.user).exists()
    if already_submitted:
        messages.info(request, 'You have already submitted this assignment.')
        return redirect('colledge_subject_assignments', subject_id=assignment.subject.id)
    if request.method == 'POST':
        form = ColledgeSubjectAssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.user = request.user
            sub.save()
            messages.success(request, 'Assignment submitted.')
            return redirect('colledge_subject_assignments', subject_id=assignment.subject.id)
    else:
        form = ColledgeSubjectAssignmentSubmissionForm()
    return render(request, 'colledge/colledge_assignment_submit.html', {
        'assignment': assignment,
        'colledge': colledge,
        'form': form,
    })
