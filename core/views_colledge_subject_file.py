from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_colledge_subject import ColledgeSubject
from .models_colledge_subject_file import ColledgeSubjectFile
from .models_colledge import ColledgeMembership
from .forms_colledge_subject_file import ColledgeSubjectFileForm

@login_required
def colledge_subject_files(request, subject_id):
    subject = get_object_or_404(ColledgeSubject, id=subject_id)
    colledge = subject.colledge_class
    is_manager = (colledge.owner == request.user)
    is_member = ColledgeMembership.objects.filter(colledge_class=colledge, user=request.user).exists() or is_manager
    if not is_member:
        return redirect('dashboard')
    files = ColledgeSubjectFile.objects.filter(subject=subject)
    if request.method == 'POST' and is_manager:
        form = ColledgeSubjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.subject = subject
            file_obj.uploaded_by = request.user
            file_obj.save()
            messages.success(request, 'File uploaded.')
            return redirect('colledge_subject_files', subject_id=subject.id)
    else:
        form = ColledgeSubjectFileForm()
    return render(request, 'colledge/colledge_subject_files.html', {
        'subject': subject,
        'colledge': colledge,
        'files': files,
        'form': form,
        'is_manager': is_manager,
    })
