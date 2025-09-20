from django import forms
from .models_colledge_subject_test_submission import ColledgeSubjectTestSubmission

class ColledgeSubjectTestGradeForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectTestSubmission
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
        }
