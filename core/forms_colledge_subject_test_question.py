from django import forms
from .models_colledge_subject_test_submission import ColledgeSubjectTestQuestion

class ColledgeSubjectTestQuestionForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectTestQuestion
        fields = ['question_text']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter question text'}),
        }
