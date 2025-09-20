from django import forms
from .models_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmission

class ColledgeSubjectAssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectAssignmentSubmission
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(),
        }
