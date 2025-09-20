from django import forms
from .models_colledge import ColledgeClass

class ColledgeClassForm(forms.ModelForm):
    class Meta:
        model = ColledgeClass
        fields = ['name', 'description', 'rules', 'max_members']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'rules': forms.Textarea(attrs={'rows': 2}),
        }
