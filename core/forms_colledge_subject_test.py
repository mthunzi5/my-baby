from django import forms
from .models_colledge_subject_test import ColledgeSubjectTest

class ColledgeSubjectTestForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectTest
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }
