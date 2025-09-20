from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models_colledge import ColledgeClass, ColledgeMembership
from .models_colledge_subject_test_submission import ColledgeSubjectTestSubmission
from .models_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmission
@login_required
def my_colledge_classes(request):
    # Classes owned by user
    owned = ColledgeClass.objects.filter(owner=request.user)
    # Classes user is a member of (excluding owned)
    member = ColledgeClass.objects.filter(memberships__user=request.user).exclude(owner=request.user)
    return render(request, 'colledge/my_colledge_classes.html', {
        'owned': owned,
        'member': member,
    })


@login_required
def my_colledge_history(request):
    user = request.user
    # Fetch test submissions for this user
    test_submissions = ColledgeSubjectTestSubmission.objects.filter(user=user).select_related('test').order_by('-submitted_at')
    # Fetch assignment submissions for this user
    assignment_submissions = ColledgeSubjectAssignmentSubmission.objects.filter(user=user).select_related('assignment').order_by('-submitted_at')
    return render(request, 'colledge/my_history.html', {
        'test_submissions': test_submissions,
        'assignment_submissions': assignment_submissions,
    })