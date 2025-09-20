from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
import dj_database_url

from django.utils import timezone
from .models_site_logo import SiteLogo


# core/models.py
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('school_admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('general', 'General User'),
    )
    GRADE_CHOICES = [
        ('Gr8', 'Grade 8'),
        ('Gr9', 'Grade 9'),
        ('Gr10', 'Grade 10'),
        ('Gr11', 'Grade 11'),
        ('Gr12', 'Grade 12'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school_id = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )

    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, null=True, blank=True)

    email = models.EmailField(unique=False, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # new field
    recovery_hint = models.CharField(max_length=100, blank=True, null=True)  # optional

    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['school_id']),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"





class Subject(models.Model):
    GRADE_CHOICES = [
        ('Gr8', 'Grade 8'),
        ('Gr9', 'Grade 9'),
        ('Gr10', 'Grade 10'),
        ('Gr11', 'Grade 11'),
        ('Gr12', 'Grade 12'),
    ]
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True)
    school_id = models.CharField(max_length=100)
    cover_image = models.ImageField(
        upload_to='subject_covers/', null=True, blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    pass_mark = models.PositiveIntegerField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    lead_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'teacher'},
        related_name='lead_subjects'
    )
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teaching_subjects', blank=True, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subjects', blank=True, limit_choices_to={'role': 'student'})

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['school_id']),
            models.Index(fields=['grade']),
        ]

class SubjectFile(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='subject_files/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'])]
    )
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


#test

class SubjectTest(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='tests', db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['date']),
        ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_auto_graded = models.BooleanField(default=True)
    is_posted = models.BooleanField(default=False)
    open = models.BooleanField(default=False)
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(default=30)  # or whatever default you want
    total_marks = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TestQuestion(models.Model):
    test = models.ForeignKey(SubjectTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])

    def __str__(self):
        return f"Question for {self.test.title}"


class StudentTestSubmission(models.Model):
    test = models.ForeignKey(SubjectTest, on_delete=models.CASCADE, related_name='submissions', db_index=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['test']),
            models.Index(fields=['student']),
        ]
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)  # in percentage
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.test.title}"


class StudentAnswer(models.Model):
    submission = models.ForeignKey(StudentTestSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])


#Discussions 
class DiscussionThread(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='threads')
    test = models.ForeignKey(SubjectTest, on_delete=models.SET_NULL, null=True, blank=True, related_name='threads')
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DiscussionMessage(models.Model):
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='messages')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # To track edits

    def __str__(self):
        return f"Message by {self.posted_by.username} on {self.thread.title}"


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('surprised', '😲'),
        ('sad', '😢'),
    ]

    message = models.ForeignKey(DiscussionMessage, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'reaction_type')


#Assignments
User = get_user_model()

class Assignment(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instruction_file = models.FileField(
        upload_to='assignments/', blank=True, null=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'])]
    )

    class Meta:
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['due_date']),
        ]
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_past_due(self):
        return timezone.now() > self.due_date

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, db_index=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    submission_file = models.FileField(
        upload_to='submissions/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )

    class Meta:
        indexes = [
            models.Index(fields=['assignment']),
            models.Index(fields=['student']),
        ]
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='graded_assignments')
    graded_at = models.DateTimeField(null=True, blank=True)

    def is_graded(self):
        return self.grade is not None

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"




####
User = get_user_model()

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='posts/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}'s Post at {self.created_at}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class ReactionP(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('wow', '😮'),
        ('laugh', '😂'),
        ('sad', '😢'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # One reaction type per user per post

    def __str__(self):
        return f"{self.user.username} reacted {self.type} on post {self.post.id}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actor_notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)  # <-- updated
    verb = models.CharField(max_length=50)  # 'commented', 'reacted'
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        if self.post:
            return f"{self.actor.username} {self.verb} on your post"
        return f"{self.actor.username} {self.verb}"


class CommentReaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
    
    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"

        


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profiles/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# --- Signal to auto-create UserProfile when a User is created ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


##Followers
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class DraftingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafts')
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(
        upload_to='draft_pdfs/',
        validators=[FileExtensionValidator(['pdf'])]
    )
    canvas_image = models.ImageField(
        upload_to='draft_canvas/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
# lab

class DraftingCanvas(models.Model):
    session = models.ForeignKey(DraftingSession, related_name='canvases', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='drafting_canvases/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Canvas for {self.session.title}"


class CanvasPage(models.Model):
    draft = models.ForeignKey(DraftingSession, related_name='pages', on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to='canvas_pages/', null=True, blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )

    class Meta:
        unique_together = ('draft', 'page_number')
        ordering = ['page_number']




#Conversions
class DocumentConversion(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    original_file = models.FileField(
        upload_to='conversions/originals/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    converted_file = models.FileField(
        upload_to='conversions/converted/', null=True, blank=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    conversion_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)