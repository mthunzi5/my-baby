from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject_test import ColledgeSubjectTest
from .models_colledge_subject_test_submission import ColledgeSubjectTestSubmission, ColledgeSubjectTestAnswer
from .forms_colledge_subject_test_grade import ColledgeSubjectTestGradeForm
from .models_colledge import ColledgeMembership

@login_required
def colledge_test_submissions(request, test_id):
    test = get_object_or_404(ColledgeSubjectTest, id=test_id)
    colledge = test.subject.colledge_class
    is_manager = (colledge.owner == request.user)
    if not is_manager:
        return redirect('dashboard')
    submissions = ColledgeSubjectTestSubmission.objects.filter(test=test)
    if request.method == 'POST':
        sub_id = request.POST.get('sub_id')
        sub = get_object_or_404(ColledgeSubjectTestSubmission, id=sub_id)
        form = ColledgeSubjectTestGradeForm(request.POST, instance=sub)
        if form.is_valid():
            graded_sub = form.save(commit=False)
            graded_sub.graded = True
            graded_sub.save()
            messages.success(request, f'Graded {sub.user.username}\'s submission.')
            return redirect('colledge_test_submissions', test_id=test.id)
    return render(request, 'colledge/colledge_test_submissions.html', {
        'test': test,
        'colledge': colledge,
        'submissions': submissions,
        'grade_form': ColledgeSubjectTestGradeForm(),
    })
