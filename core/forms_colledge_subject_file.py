from django import forms
from .models_colledge_subject_file import ColledgeSubjectFile

class ColledgeSubjectFileForm(forms.ModelForm):
    class Meta:
        model = ColledgeSubjectFile
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Optional description'}),
        }
