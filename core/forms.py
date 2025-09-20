from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils import timezone
from django.forms import DateTimeInput

from .models import User,DocumentConversion, Subject, SubjectFile,UserProfile,DraftingSession, SubjectTest,ReactionP, TestQuestion, DiscussionThread, DiscussionMessage, Assignment, AssignmentSubmission, Post, Comment

class SchoolAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash password
        user.role = 'school_admin'
        if commit:
            user.save()
        return user
class TeacherCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash password
        user.role = 'teacher'
        if commit:
            user.save()
        return user


class SchoolUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=(('student', 'Student'), ('teacher', 'Teacher')))
    grade = forms.ChoiceField(choices=User.GRADE_CHOICES, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'grade', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description', 'cover_image', 'pass_mark', 'duration', 'lead_teacher', 'grade']  # <-- Add 'grade'

class SubjectFileForm(forms.ModelForm):
    class Meta:
        model = SubjectFile
        fields = ['title', 'file']


# forms.py
class TestForm(forms.ModelForm):
    class Meta:
        model = SubjectTest
        fields = ['title', 'description', 'is_auto_graded', 'date', 'duration_minutes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Duration in minutes'}),
        }

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date < timezone.now().date():
            raise forms.ValidationError("Test date cannot be in the past.")
        return selected_date



class QuestionForm(forms.ModelForm):
    class Meta:
        model = TestQuestion
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']


#Discussions
class DiscussionThreadForm(forms.ModelForm):
    class Meta:
        model = DiscussionThread
        fields = ['title']

class DiscussionMessageForm(forms.ModelForm):
    class Meta:
        model = DiscussionMessage
        fields = ['content']  # ✅ This matches your model
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your reply...'}),
        }



class MessageForm(forms.ModelForm):
    class Meta:
        model = DiscussionMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }



#Assignments
class AssignmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Due Date and Time"
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'instruction_file', 'due_date']


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional comment...'})
        }

class GeneralUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'general'
        if commit:
            user.save()
        return user




####Socials
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What’s on your mind?'}),
        }


# forms.py
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent']  # allow nested replies
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2}),
            'parent': forms.HiddenInput(),
        }


# Combines user and profile fields for editing
class UserAccountProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep current password.")

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'address', 'phone']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

    def save(self, commit=True, user=None):
        profile = super().save(commit=False)
        if user:
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            pwd = self.cleaned_data.get('password')
            if pwd:
                user.set_password(pwd)
            if commit:
                user.save()
        if commit:
            profile.save()
        return profile




class DraftingSessionForm(forms.ModelForm):
    class Meta:
        model = DraftingSession
        fields = ['title', 'pdf_file']



###
### Recover account 

#class UsernameRecoveryForm(forms.Form):
 #   email = forms.EmailField(label="Enter your registered email")



#from django import forms

class UsernameRecoveryForm(forms.Form):
    email = forms.EmailField(label="Your email address")



#Conversions

CONVERSION_CHOICES = [
    ('pdf2docx', 'PDF to Word (.docx)'),
    ('docx2pdf', 'Word (.docx) to PDF'),
    ('pdf2ocr', 'OCR (Extract text from PDF)'),
]

class DocumentConversionForm(forms.Form):
    conversion_type = forms.ChoiceField(choices=CONVERSION_CHOICES)
    file = forms.FileField()

