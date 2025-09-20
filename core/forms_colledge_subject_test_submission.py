from django import forms
from .models_colledge_subject_test_submission import ColledgeSubjectTestSubmission, ColledgeSubjectTestAnswer

class ColledgeSubjectTestSubmissionForm(forms.Form):
    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        if questions:
            for q in questions:
                self.fields[f'q_{q.id}'] = forms.CharField(
                    label=q.question_text,
                    widget=forms.Textarea(attrs={'rows': 2}),
                    required=True
                )
