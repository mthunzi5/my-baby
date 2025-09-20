from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models_colledge import ColledgeClass, ColledgeMembership
from .forms_colledge_member import AddColledgeMemberForm

from .models_colledge_subject_test_submission import ColledgeSubjectTestSubmission
from .models_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmission

User = get_user_model()

@login_required
def colledge_dashboard(request, colledge_id):
    from django.utils import timezone
    colledge = get_object_or_404(ColledgeClass, id=colledge_id)
    is_owner = (colledge.owner == request.user)
    members = User.objects.filter(colledge_memberships__colledge_class=colledge)
    # Auto-deactivate if expired
    if colledge.is_active and colledge.expires_at and timezone.now() > colledge.expires_at:
        colledge.is_active = False
        colledge.save()
    can_add = is_owner and colledge.is_active and members.count() < colledge.max_members
    add_form = None
    if can_add:
        if request.method == 'POST' and 'add_member' in request.POST:
            add_form = AddColledgeMemberForm(request.POST, colledge_class=colledge)
            if add_form.is_valid():
                user = User.objects.get(email=add_form.cleaned_data['email'])
                ColledgeMembership.objects.create(colledge_class=colledge, user=user)
                messages.success(request, f"{user.username} added to class.")
                return redirect('colledge_dashboard', colledge_id=colledge.id)
        else:
            add_form = AddColledgeMemberForm(colledge_class=colledge)
    # Calculate countdown (seconds left)
    countdown = None
    if colledge.is_active and colledge.expires_at:
        delta = colledge.expires_at - timezone.now()
        countdown = int(delta.total_seconds()) if delta.total_seconds() > 0 else 0
    return render(request, 'colledge/colledge_dashboard.html', {
        'colledge': colledge,
        'members': members,
        'is_owner': is_owner,
        'can_add': can_add,
        'add_form': add_form,
        'countdown': countdown,
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