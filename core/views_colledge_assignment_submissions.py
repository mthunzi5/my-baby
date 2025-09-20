from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject_assignment import ColledgeSubjectAssignment
from .models_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmission
from .forms_colledge_subject_assignment_grade import ColledgeSubjectAssignmentGradeForm
from .models_colledge import ColledgeMembership

@login_required
def colledge_assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(ColledgeSubjectAssignment, id=assignment_id)
    colledge = assignment.subject.colledge_class
    is_manager = (colledge.owner == request.user)
    if not is_manager:
        return redirect('dashboard')
    submissions = ColledgeSubjectAssignmentSubmission.objects.filter(assignment=assignment)
    if request.method == 'POST':
        sub_id = request.POST.get('sub_id')
        sub = get_object_or_404(ColledgeSubjectAssignmentSubmission, id=sub_id)
        form = ColledgeSubjectAssignmentGradeForm(request.POST, instance=sub)
        if form.is_valid():
            graded_sub = form.save(commit=False)
            graded_sub.graded = True
            graded_sub.save()
            messages.success(request, f'Graded {sub.user.username}\'s submission.')
            return redirect('colledge_assignment_submissions', assignment_id=assignment.id)
    return render(request, 'colledge/colledge_assignment_submissions.html', {
        'assignment': assignment,
        'colledge': colledge,
        'submissions': submissions,
        'grade_form': ColledgeSubjectAssignmentGradeForm(),
    })
