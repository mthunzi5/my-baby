
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject import ColledgeSubject
from .models_colledge_subject_test import ColledgeSubjectTest
from .models_colledge import ColledgeMembership
from .forms_colledge_subject_test import ColledgeSubjectTestForm

@login_required
@require_POST
def colledge_test_open(request, test_id):
    test = get_object_or_404(ColledgeSubjectTest, id=test_id)
    colledge = test.subject.colledge_class
    if colledge.owner != request.user:
        return redirect('dashboard')
    test.open = True
    test.save()
    messages.success(request, f'Test "{test.name}" is now open.')
    return redirect('colledge_subject_tests', subject_id=test.subject.id)

@login_required
@require_POST
def colledge_test_close(request, test_id):
    test = get_object_or_404(ColledgeSubjectTest, id=test_id)
    colledge = test.subject.colledge_class
    if colledge.owner != request.user:
        return redirect('dashboard')
    test.open = False
    test.save()
    messages.success(request, f'Test "{test.name}" is now closed.')
    return redirect('colledge_subject_tests', subject_id=test.subject.id)

@login_required
def colledge_subject_tests(request, subject_id):
    subject = get_object_or_404(ColledgeSubject, id=subject_id)
    colledge = subject.colledge_class
    is_manager = (colledge.owner == request.user)
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or is_manager
    if not is_member:
        return redirect('dashboard')
    tests = ColledgeSubjectTest.objects.filter(subject=subject)
    if request.method == 'POST' and is_manager:
        form = ColledgeSubjectTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.subject = subject
            test.created_by = request.user
            test.save()
            messages.success(request, 'Test created.')
            return redirect('colledge_subject_tests', subject_id=subject.id)
    else:
        form = ColledgeSubjectTestForm()
    return render(request, 'colledge/colledge_subject_tests.html', {
        'subject': subject,
        'colledge': colledge,
        'tests': tests,
        'form': form,
        'is_manager': is_manager,
    })
