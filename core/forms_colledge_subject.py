from django import forms
from .models_colledge_subject import ColledgeSubject

class ColledgeSubjectForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubject
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }
