from django import forms
from .models_colledge_subject_assignment_submission import ColledgeSubjectAssignmentSubmission

class ColledgeSubjectAssignmentGradeForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectAssignmentSubmission
        fields = ['grade', 'feedback']
        widgets = {
            'grade': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'feedback': forms.Textarea(attrs={'rows': 2}),
        }
