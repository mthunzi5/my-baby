from django import forms
from .models_colledge_subject_assignment import ColledgeSubjectAssignment

class ColledgeSubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectAssignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
