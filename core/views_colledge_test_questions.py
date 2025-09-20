from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject_test import ColledgeSubjectTest
from .models_colledge_subject_test_submission import ColledgeSubjectTestQuestion
from .forms_colledge_subject_test_question import ColledgeSubjectTestQuestionForm
from .models_colledge import ColledgeMembership

@login_required
def colledge_test_questions(request, test_id):
    test = get_object_or_404(ColledgeSubjectTest, id=test_id)
    colledge = test.subject.colledge_class
    is_manager = (colledge.owner == request.user)
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or is_manager
    if not is_manager:
        return redirect('dashboard')
    questions = ColledgeSubjectTestQuestion.objects.filter(test=test)
    if request.method == 'POST':
        form = ColledgeSubjectTestQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.test = test
            q.save()
            messages.success(request, 'Question added.')
            return redirect('colledge_test_questions', test_id=test.id)
    else:
        form = ColledgeSubjectTestQuestionForm()
    return render(request, 'colledge/colledge_test_questions.html', {
        'test': test,
        'colledge': colledge,
        'questions': questions,
        'form': form,
        'is_manager': is_manager,
    })
