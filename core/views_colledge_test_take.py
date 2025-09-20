from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject_test import ColledgeSubjectTest
from .models_colledge_subject_test_submission import ColledgeSubjectTestQuestion, ColledgeSubjectTestSubmission, ColledgeSubjectTestAnswer
from .forms_colledge_subject_test_submission import ColledgeSubjectTestSubmissionForm
from .models_colledge import ColledgeMembership

@login_required
def colledge_test_take(request, test_id):
    test = get_object_or_404(ColledgeSubjectTest, id=test_id)
    colledge = test.subject.colledge_class
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or (colledge.owner == request.user)
    if not is_member:
        return redirect('dashboard')
    already_submitted = ColledgeSubjectTestSubmission.objects.filter(test=test, user=request.user).exists()
    questions = ColledgeSubjectTestQuestion.objects.filter(test=test)
    if already_submitted:
        messages.info(request, 'You have already submitted this test.')
        return redirect('colledge_subject_tests', subject_id=test.subject.id)
    if request.method == 'POST':
        form = ColledgeSubjectTestSubmissionForm(request.POST, questions=questions)
        if form.is_valid():
            submission = ColledgeSubjectTestSubmission.objects.create(test=test, user=request.user)
            for q in questions:
                ColledgeSubjectTestAnswer.objects.create(
                    submission=submission,
                    question=q,
                    answer_text=form.cleaned_data[f'q_{q.id}']
                )
            messages.success(request, 'Test submitted.')
            return redirect('colledge_subject_tests', subject_id=test.subject.id)
    else:
        form = ColledgeSubjectTestSubmissionForm(questions=questions)
    return render(request, 'colledge/colledge_test_take.html', {
        'test': test,
        'colledge': colledge,
        'form': form,
        'questions': questions,
    })
