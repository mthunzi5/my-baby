from django import forms
from django.contrib.auth import get_user_model
from .models_colledge import ColledgeMembership

User = get_user_model()

class AddColledgeMemberForm(forms.Form):
    email = forms.EmailField(label="User Email")

    def __init__(self, *args, **kwargs):
        self.colledge_class = kwargs.pop('colledge_class', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No registered user with this email.")
        # Check if already a member
        if ColledgeMembership.objects.filter(colledge_class=self.colledge_class, user=user).exists():
            raise forms.ValidationError("User is already a member of this class.")
        return email
