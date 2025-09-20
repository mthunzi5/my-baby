from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
import uuid
import random
import datetime
from django.db.models import Q
from django.conf import settings
from collections import defaultdict
from django.db.models import Avg, Count
from django.utils import timezone
from .forms import SchoolAdminCreationForm,DocumentConversionForm,  UsernameRecoveryForm, DraftingSessionForm, UserAccountProfileForm, PostForm,CommentForm,ReactionP, SchoolUserCreationForm,GeneralUserRegistrationForm, SubjectForm, SubjectFileForm, TestForm, QuestionForm, DiscussionMessageForm, DiscussionThreadForm, MessageForm, AssignmentForm, AssignmentSubmissionForm
from .models import CommentReaction, User,UserProfile,Follow,DraftingCanvas,DocumentConversion,   CanvasPage, Reaction,DraftingSession, ReactionP,Notification,Post,Comment, Subject, SubjectFile, SubjectTest, TestQuestion, StudentTestSubmission, StudentAnswer, DiscussionThread, DiscussionMessage, Assignment, AssignmentSubmission # Assuming your User model is in the same app's models.py
import zipfile
import os
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404
from io import BytesIO
from django.http import HttpResponse
import base64
from django.core.files.base import ContentFile
from django.core.mail import send_mail, get_connection
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from allauth.socialaccount.providers import registry
from allauth.socialaccount.models import SocialApp
import ssl
import certifi

from pdf2docx import Converter
from docx2pdf import convert as docx2pdf_convert
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import tempfile
from .forms_bulk_email import BulkEmailForm



# Helper function to check if the user is an admin
def is_admin_or_superuser(user):
    return user.is_authenticated and (getattr(user, 'role', None) == 'admin' or user.is_superuser)

def send_welcome_email(user):
    subject = "Welcome to Global Future!"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "Welcome to Global Future, your new learning management system.\n"
        "We're excited to have you as part of our community!\n\n"
        "If you have any questions, feel free to reach out.\n\n"
        "Best regards,\n"
        "The Global Future Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


@login_required
def dashboard(request):
    user = request.user
    
    # ...existing code...
    
    if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
        # Admin Dashboard Statistics
        
        # Overall user statistics
        total_users = User.objects.count()
        total_school_admins = User.objects.filter(role='school_admin').count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_students = User.objects.filter(role='student').count()
        total_general_users = User.objects.filter(role='general').count()
        
        # School statistics - Fixed to use only existing fields
        schools = User.objects.filter(role='school_admin').values('school_id', 'first_name', 'last_name', 'username').distinct()
        school_stats = []
        
        for school in schools:
            school_id = school['school_id']
            # Create a school name from available data
            if school['first_name'] and school['last_name']:
                school_name = f"{school['first_name']} {school['last_name']}'s School"
            else:
                school_name = f"{school['username']}'s School"
            
            teachers_count = User.objects.filter(school_id=school_id, role='teacher').count()
            students_count = User.objects.filter(school_id=school_id, role='student').count()
            subjects_count = Subject.objects.filter(school_id=school_id).count()
            
            # Only include these if the models exist and have the right relationships
            try:
                tests_count = SubjectTest.objects.filter(subject__school_id=school_id).count()
            except:
                tests_count = 0
                
            try:
                assignments_count = Assignment.objects.filter(subject__school_id=school_id).count()
            except:
                assignments_count = 0
            
            school_stats.append({
                'school_id': school_id,
                'school_name': school_name,
                'teachers': teachers_count,
                'students': students_count,
                'total_users': teachers_count + students_count,
                'subjects': subjects_count,
                'tests': tests_count,
                'assignments': assignments_count,
            })
        
        # Universal subject statistics
        total_subjects = Subject.objects.count()
        try:
            total_tests = SubjectTest.objects.count()
        except:
            total_tests = 0
            
        try:
            total_assignments = Assignment.objects.count()
        except:
            total_assignments = 0
        
        # Recent activity
        recent_schools = User.objects.filter(role='school_admin').order_by('-date_joined')[:5]
        try:
            recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
        except:
            recent_posts = []
        
        context = {
            'total_users': total_users,
            'total_school_admins': total_school_admins,
            'total_teachers': total_teachers,
            'total_students': total_students,
            'total_general_users': total_general_users,
            'school_stats': school_stats,
            'total_subjects': total_subjects,
            'total_tests': total_tests,
            'total_assignments': total_assignments,
            'recent_schools': recent_schools,
            'recent_posts': recent_posts,
        }
        
        return render(request, 'dashboard_admin.html', context)

    # Check if the user object has a 'role' attribute before accessing it
    if hasattr(user, 'role'):
        if user.role == 'school_admin':
            return school_admin_dashboard(request)  # Use the new function
        elif user.role == 'teacher':
            return render(request, 'dashboard_teacher.html')
        elif user.role == 'student':
            # Student dashboard context
            subjects = user.subjects.all()
            # Recent assignments (last 5, not past due)
            from django.utils import timezone
            now = timezone.now()
            recent_assignments = []
            upcoming_tests = []
            if subjects.exists():
                recent_assignments = Assignment.objects.filter(subject__in=subjects, due_date__gte=now).order_by('due_date')[:5]
                upcoming_tests = SubjectTest.objects.filter(subject__in=subjects, date__gte=now).order_by('date')[:5]
            # Announcements (last 5)
            try:
                announcements = Post.objects.filter(is_announcement=True).order_by('-created_at')[:5]
            except:
                announcements = []
            return render(request, 'dashboard_student.html', {
                'recent_assignments': recent_assignments,
                'upcoming_tests': upcoming_tests,
                'announcements': announcements,
            })
        elif user.role == 'general':
            return render(request, 'users/general_dashboard.html')
        else:
            return redirect('/accounts/login/')
    else:
        return redirect('/accounts/login/')





# Replace the school_admin_dashboard function with this corrected version

@login_required
def school_admin_dashboard(request):
    user = request.user
    
    if user.role != 'school_admin':
        return redirect('dashboard')
    
    school_id = user.school_id
    
    # Basic statistics for this school only
    total_teachers = User.objects.filter(school_id=school_id, role='teacher').count()
    total_students = User.objects.filter(school_id=school_id, role='student').count()
    total_subjects = Subject.objects.filter(school_id=school_id).count()
    
    # Grade-wise student distribution
    grade_distribution = {}
    for grade in range(1, 13):  
        count = User.objects.filter(school_id=school_id, role='student', grade=grade).count()
        if count > 0:
            grade_distribution[f"Grade {grade}"] = count
    
    # Subject statistics
    subject_stats = []
    subjects = Subject.objects.filter(school_id=school_id)
    for subject in subjects:
        teachers_count = subject.teachers.count()
        students_count = subject.students.count()
        
        try:
            tests_count = SubjectTest.objects.filter(subject=subject).count()
        except:
            tests_count = 0
            
        try:
            assignments_count = Assignment.objects.filter(subject=subject).count()
        except:
            assignments_count = 0
        
        subject_stats.append({
            'name': subject.name,
            'grade': subject.grade,
            'teachers': teachers_count,
            'students': students_count,
            'tests': tests_count,
            'assignments': assignments_count,
        })
    
    # Top 5 performers per grade
    top_performers_by_grade = {}
    for grade in range(1, 13):
        students_in_grade = User.objects.filter(
            school_id=school_id, 
            role='student', 
            grade=grade
        )
        
        if students_in_grade.exists():
            student_averages = []
            
            for student in students_in_grade:
                # Get all subjects for this student's grade
                student_subjects = Subject.objects.filter(
                    school_id=school_id,
                    grade=grade,
                    students=student
                )
                
                if student_subjects.exists():
                    total_grade = 0
                    total_submissions = 0
                    
                    for subject in student_subjects:
                        # Get test submissions for this subject
                        try:
                            test_submissions = StudentTestSubmission.objects.filter(
                                student=student,
                                test__subject=subject,
                                is_graded=True
                            )
                            
                            for submission in test_submissions:
                                if submission.grade is not None:
                                    total_grade += submission.grade
                                    total_submissions += 1
                        except:
                            pass
                        
                        # Get assignment submissions for this subject
                        try:
                            assignment_submissions = AssignmentSubmission.objects.filter(
                                student=student,
                                assignment__subject=subject,
                                grade__isnull=False
                            )
                            
                            for submission in assignment_submissions:
                                if submission.grade:
                                    total_grade += float(submission.grade)
                                    total_submissions += 1
                        except:
                            pass
                    
                    if total_submissions > 0:
                        average = total_grade / total_submissions
                        student_averages.append({
                            'student': student,
                            'average': round(average, 2),
                            'total_submissions': total_submissions
                        })
            
            # Sort by average and get top 5
            student_averages.sort(key=lambda x: x['average'], reverse=True)
            top_performers_by_grade[f"Grade {grade}"] = student_averages[:5]
    
    # Recent activity in this school - Fixed field names
    try:
        recent_tests = SubjectTest.objects.filter(
            subject__school_id=school_id
        ).order_by('-date')[:5]  # Changed from 'created_at' to 'date'
    except:
        recent_tests = []
    
    try:
        # Check if Assignment model has created_at field, if not use another field
        recent_assignments = Assignment.objects.filter(
            subject__school_id=school_id
        ).order_by('-id')[:5]  # Using id as fallback ordering
    except:
        recent_assignments = []
    
    recent_users = User.objects.filter(
        school_id=school_id
    ).exclude(role='school_admin').order_by('-date_joined')[:5]
    
    # Teacher workload (subjects per teacher)
    teacher_workload = []
    teachers = User.objects.filter(school_id=school_id, role='teacher')
    for teacher in teachers:
        try:
            subject_count = teacher.teaching_subjects.filter(school_id=school_id).count()
            student_count = User.objects.filter(
                school_id=school_id,
                role='student',
                subjects__teachers=teacher
            ).distinct().count()
        except:
            subject_count = 0
            student_count = 0
        
        teacher_workload.append({
            'teacher': teacher,
            'subjects': subject_count,
            'students': student_count
        })
    
    # Sort by workload
    teacher_workload.sort(key=lambda x: x['subjects'], reverse=True)
    
    context = {
        'school_name': f"{user.first_name} {user.last_name}'s School" if user.first_name else f"{user.username}'s School",
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_subjects': total_subjects,
        'grade_distribution': grade_distribution,
        'subject_stats': subject_stats,
        'top_performers_by_grade': top_performers_by_grade,
        'recent_tests': recent_tests,
        'recent_assignments': recent_assignments,
        'recent_users': recent_users,
        'teacher_workload': teacher_workload,
    }
    
    return render(request, 'dashboard_school_admin.html', context)





@login_required
def create_school_admin(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard')

    if request.method == 'POST':
        form = SchoolAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'school_admin'
            user.school_id = str(uuid.uuid4())  # Generate unique ID
            user.set_password(form.cleaned_data['password'])
            user.save()
            send_welcome_email(user)
            return redirect('list_school_admins')
    else:
        form = SchoolAdminCreationForm()
    return render(request, 'admin/create_school_admin.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def list_school_admins(request):
    school_admins = User.objects.filter(role='school_admin')
    return render(request, 'school_admin_list.html', {'school_admins': school_admins})

@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def edit_school_admin(request, user_id):
    school_admin = get_object_or_404(User, id=user_id, role='school_admin')
    if request.method == 'POST':
        form = SchoolAdminCreationForm(request.POST, instance=school_admin)
        if form.is_valid():
            form.save()
            messages.success(request, "School admin updated successfully.")
            return redirect('list_school_admins')
    else:
        form = SchoolAdminCreationForm(instance=school_admin)
    return render(request, 'edit_school_admin.html', {'form': form})

# Delete school admin
@login_required
@user_passes_test(lambda u: u.role == 'admin' or u.is_superuser)
def delete_school_admin(request, user_id):
    school_admin = get_object_or_404(User, id=user_id, role='school_admin')
    school_admin.delete()
    messages.success(request, "School admin deleted.")
    return redirect('list_school_admins')







# Check if school_admin
def is_school_admin(user):
    return user.is_authenticated and user.role == 'school_admin'

# Create user (teacher or student)
@login_required
def create_school_user(request):
    if request.user.role != 'school_admin':
        return redirect('dashboard')

    if request.method == 'POST':
        #form = SchoolUserCreationForm(request.POST)
        form = SchoolUserCreationForm(request.POST, request.FILES)  # <-- add request.FILES
        if form.is_valid():
            user = form.save(commit=False)
            user.school_id = request.user.school_id  # Inherit school ID
            user.save()
            return redirect('list_school_users')
    else:
        form = SchoolUserCreationForm()
        
    return render(request, 'school_admin/create_user.html', {'form': form})








# List all teachers and students
@login_required
def list_school_users(request):
    if request.user.role != 'school_admin':
        return redirect('dashboard')

    users = User.objects.filter(school_id=request.user.school_id).exclude(role='school_admin')
    return render(request, 'school_admin/user_list.html', {'users': users})

# Edit user
@login_required
@user_passes_test(is_school_admin)
def edit_school_user(request, user_id):
    user = get_object_or_404(User, id=user_id, role__in=['teacher', 'student'])
    if request.method == 'POST':
        #form = SchoolUserCreationForm(request.POST, instance=user)
        form = SchoolUserCreationForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('list_school_users')
    else:
        form = SchoolUserCreationForm(instance=user)
    return render(request, 'edit_school_user.html', {'form': form})

# Delete user
@login_required
@user_passes_test(is_school_admin)
def delete_school_user(request, user_id):
    user = get_object_or_404(User, id=user_id, role__in=['teacher', 'student'])
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('list_school_users')


@login_required
def subject_list(request):
    subjects = Subject.objects.filter(school_id=request.user.school_id)
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})

@login_required
def subject_create(request):
    if request.user.role != 'school_admin':
        return redirect('dashboard')
    if request.method == 'POST':
        #form = SubjectForm(request.POST)
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.school_id = request.user.school_id
            subject.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'subjects/subject_form.html', {'form': form})

@login_required
def subject_edit(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, school_id=request.user.school_id)
    #form = SubjectForm(request.POST or None, instance=subject)
    form = SubjectForm(request.POST or None, request.FILES or None, instance=subject)
    if form.is_valid():
        form.save()
        return redirect('subject_list')
    return render(request, 'subjects/subject_form.html', {'form': form})

@login_required
def subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, school_id=request.user.school_id)
    subject.delete()
    return redirect('subject_list')

@login_required
def subject_manage_users(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, school_id=request.user.school_id)
    teachers = User.objects.filter(role='teacher', school_id=request.user.school_id)
    # Only students with the same grade as the subject
    students = User.objects.filter(
        role='student',
        school_id=request.user.school_id,
        grade=subject.grade
    )

    if request.method == 'POST':
        teacher_ids = request.POST.getlist('teachers')
        student_ids = request.POST.getlist('students')
        subject.teachers.set(teacher_ids)
        subject.students.set(student_ids)
        return redirect('subject_list')

    return render(request, 'subjects/subject_manage_users.html', {
        'subject': subject,
        'teachers': teachers,
        'students': students,
    })


@login_required
def my_subjects(request):
    if request.user.role == 'teacher':
        subjects = request.user.teaching_subjects.filter(school_id=request.user.school_id)
    elif request.user.role == 'student':
        subjects = request.user.subjects.filter(school_id=request.user.school_id)
    else:
        subjects = []

    return render(request, 'users/my_subjects.html', {'subjects': subjects})


#FilesUpload
@login_required
def upload_subject_file(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    subjects = Subject.objects.filter(teachers=request.user)

    if request.method == 'POST':
        form = SubjectFileForm(request.POST, request.FILES)
        form.fields['subject'].queryset = subjects
        if form.is_valid():
            subject_file = form.save(commit=False)
            subject_file.uploaded_by = request.user
            subject_file.save()
            messages.success(request, "File uploaded successfully.")
            return redirect('my_subject_files')
    else:
        form = SubjectFileForm()
        form.fields['subject'].queryset = subjects

    return render(request, 'files/upload_file.html', {'form': form})

@login_required
def view_subject_files(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.user.role == 'teacher' and request.user not in subject.teachers.all():
        return redirect('dashboard')

    if request.user.role == 'student' and request.user not in subject.students.all():
        return redirect('dashboard')

    files = subject.files.all()
    return render(request, 'files/view_subject_files.html', {'subject': subject, 'files': files})

@login_required
def my_subject_files(request):
    files = SubjectFile.objects.filter(uploaded_by=request.user)
    return render(request, 'files/my_uploaded_files.html', {'files': files})


@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, school_id=request.user.school_id)

    # Check access
    if request.user.role == 'teacher' and request.user not in subject.teachers.all():
        return redirect('my_subjects')
    if request.user.role == 'student' and request.user not in subject.students.all():
        return redirect('my_subjects')

    return render(request, 'subjects/subject_detail.html', {
        'subject': subject,
        'user_role': request.user.role
    })


@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, school_id=request.user.school_id)

    # Filter files by subject and uploaded_by if teacher
    if request.user.role == 'teacher':
        files = subject.files.filter(uploaded_by=request.user)
    else:
        files = subject.files.all()

    return render(request, 'subjects/subject_detail.html', {
        'subject': subject,
        'files': files
    })


@login_required
def upload_subject_file(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, teachers=request.user)

    if request.method == 'POST':
        form = SubjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.subject = subject
            file_instance.uploaded_by = request.user
            file_instance.save()
            return redirect('subject_detail', subject_id=subject.id)
    else:
        form = SubjectFileForm()
    return render(request, 'subjects/upload_file.html', {'form': form, 'subject': subject})


@login_required
def delete_subject_file(request, subject_id, file_id):
    subject = get_object_or_404(Subject, id=subject_id, school_id=request.user.school_id)
    file = get_object_or_404(SubjectFile, id=file_id, subject=subject)

    # Only uploader can delete
    if request.user == file.uploaded_by or request.user.role == 'school_admin':
        file.delete()
    return redirect('subject_detail', subject_id=subject.id)



#Test 
#Teacher 
# Helper
def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'


@login_required
@user_passes_test(is_teacher)
def create_test(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, teachers=request.user)
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.subject = subject
            test.created_by = request.user
            test.save()
            messages.success(request, "Test created successfully.")
            return redirect('add_questions', test_id=test.id)
    else:
        form = TestForm()
    return render(request, 'tests/create_test.html', {'form': form, 'subject': subject})


@login_required
@user_passes_test(is_teacher)
def add_questions(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, created_by=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            messages.success(request, "Question added.")
            return redirect('add_questions', test_id=test.id)
    else:
        form = QuestionForm()
    questions = test.questions.all()
    can_post = questions.exists()  # True if at least one question
    return render(request, 'tests/add_questions.html', {
        'form': form,
        'test': test,
        'questions': questions,
        'can_post': can_post,  # Pass to template
    })

@login_required
@user_passes_test(is_teacher)
def post_test(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, created_by=request.user)
    test.is_posted = True
    test.save()
    messages.success(request, "Test posted.")
    return redirect('subject_detail', subject_id=test.subject.id)


@login_required
@user_passes_test(is_teacher)
def open_test(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, created_by=request.user)
    test.open = True
    test.save()
    messages.success(request, "Test opened.")
    return redirect('subject_detail', subject_id=test.subject.id)


@login_required
@user_passes_test(is_teacher)
def close_test(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, created_by=request.user)
    test.open = False
    test.save()
    messages.success(request, "Test closed.")
    return redirect('subject_detail', subject_id=test.subject.id)


@login_required
@user_passes_test(is_teacher)
def view_test_submissions(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, created_by=request.user)
    submissions = test.submissions.all()
    return render(request, 'tests/view_submissions.html', {'test': test, 'submissions': submissions})


@login_required
@user_passes_test(is_teacher)
def auto_grade_submission(request, submission_id):
    submission = get_object_or_404(StudentTestSubmission, id=submission_id)
    if not submission.test.is_auto_graded:
        messages.error(request, "This test is manual.")
        return redirect('view_submissions', test_id=submission.test.id)

    correct = 0
    total = submission.answers.count()
    for answer in submission.answers.all():
        if answer.selected_answer == answer.question.correct_answer:
            correct += 1
    submission.grade = (correct / total) * 100
    submission.is_graded = True
    submission.save()
    messages.success(request, f"Auto graded: {submission.grade:.1f}%")
    return redirect('view_submissions', test_id=submission.test.id)


@login_required
@user_passes_test(is_teacher)
def manual_grade_submission(request, submission_id):
    submission = get_object_or_404(StudentTestSubmission, id=submission_id)
    if submission.test.is_auto_graded:
        messages.error(request, "This test is auto-graded.")
        return redirect('view_submissions', test_id=submission.test.id)

    if request.method == 'POST':
        total = submission.answers.count()
        correct = 0
        for answer in submission.answers.all():
            correct_answer = request.POST.get(f'q{answer.question.id}')
            if correct_answer == answer.question.correct_answer:
                correct += 1
        submission.grade = (correct / total) * 100
        submission.is_graded = True
        submission.save()
        messages.success(request, f"Manually graded: {submission.grade:.1f}%")
        return redirect('view_submissions', test_id=submission.test.id)

    return render(request, 'tests/manual_grade.html', {'submission': submission})


#StudentTest
@login_required
def write_test(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, is_posted=True, open=True)

    # Block if already submitted
    if StudentTestSubmission.objects.filter(test=test, student=request.user).exists():
        messages.warning(request, "You've already written this test.")
        return redirect('my_tests')

    duration = getattr(test, 'duration_minutes', 30)


    if request.method == 'POST':
        # Prevent double submission
        if StudentTestSubmission.objects.filter(test=test, student=request.user).exists():
            messages.warning(request, "You've already written this test.")
            return redirect('my_tests')

        answers = {}
        for question in test.questions.all():
            selected = request.POST.get(f'q{question.id}')
            if selected:
                answers[question] = selected
        submission = StudentTestSubmission.objects.create(test=test, student=request.user)
        for question, selected in answers.items():
            StudentAnswer.objects.create(
                submission=submission,
                question=question,
                selected_answer=selected
            )
        messages.success(request, "Test submitted.")
        return redirect('my_tests')

    return render(request, 'tests/write_test.html', {
        'test': test,
        'post_data': request.POST,
        'duration': duration,
    })
    


@login_required
def subject_tests(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    tests = SubjectTest.objects.filter(subject=subject)
    return render(request, 'tests/subject_tests.html', {
        'subject': subject,
        'tests': tests,
    })


@login_required
def my_tests(request):
    submissions = StudentTestSubmission.objects.filter(student=request.user).select_related('test', 'test__subject')
    return render(request, 'tests/my_tests.html', {'submissions': submissions})

@login_required
def manual_grade(request, submission_id):
    submission = get_object_or_404(StudentTestSubmission, id=submission_id)
    
    if request.method == 'POST':
        total = submission.answers.count()
        correct = 0
        missing = []
        for answer in submission.answers.all():
            correct_answer = answer.question.correct_answer
            selected = request.POST.get(f'answer_{answer.id}')
            if selected is None or selected == '':
                missing.append(answer)
            else:
                answer.selected_answer = selected
                answer.save()
                if selected == correct_answer:
                    correct += 1

        if missing:
            messages.error(request, "Please provide an answer for all questions before submitting.")
            return render(request, 'tests/manual_grade.html', {
                'submission': submission,
                'answers': submission.answers.all()
            })

        submission.grade = (correct / total) * 100 if total > 0 else 0
        submission.is_graded = True
        submission.save()
        messages.success(request, "Student test graded successfully.")
        return redirect('view_submissions', test_id=submission.test.id)

    return render(request, 'tests/manual_grade.html', {
        'submission': submission,
        'answers': submission.answers.all()
    })


@login_required
def grade_all_auto(request, test_id):
    test = get_object_or_404(SubjectTest, id=test_id, created_by=request.user)

    if not test.is_auto_graded:
        messages.error(request, "This test is not set to auto-grade.")
        return redirect('view_submissions', test_id=test_id)

    submissions = test.submissions.filter(is_graded=False)

    for submission in submissions:
        total_questions = test.questions.count()
        correct = 0
        for answer in submission.answers.all():
            if answer.selected_answer == answer.question.correct_answer:
                correct += 1
        if total_questions > 0:
            grade = (correct / total_questions) * 100
        else:
            grade = 0
        submission.grade = grade
        submission.is_graded = True
        submission.save()

    messages.success(request, "All student submissions have been auto-graded.")
    return redirect('view_test_submissions', test_id=test_id)

#Analytics
@login_required
def student_analytics(request):
    user = request.user
    if user.role != 'student':
        return redirect('dashboard')

    submissions = StudentTestSubmission.objects.filter(student=user, is_graded=True).select_related('test__subject')

    weekly_data = defaultdict(lambda: defaultdict(list))  # subject -> week -> grades

    for sub in submissions:
        week = sub.submitted_at.strftime("%Y-W%U")
        subject = sub.test.subject.name
        weekly_data[subject][week].append(sub.grade)

    # Calculate weekly averages per subject
    chart_data = {
        subject: {
            week: round(sum(grades) / len(grades), 2)
            for week, grades in weeks.items()
        }
        for subject, weeks in weekly_data.items()
    }

    return render(request, 'analytics/student_analytics.html', {
        'chart_data': chart_data
    })




@login_required
def teacher_analytics(request):
    user = request.user
    if user.role != 'teacher':
        return redirect('dashboard')

    # Get all subjects this teacher teaches
    subjects = user.teaching_subjects.all()

    subject_averages = []
    subject_chart_data = {}
    top_students_by_subject = {}

    for subject in subjects:
        tests = SubjectTest.objects.filter(subject=subject)
        submissions = StudentTestSubmission.objects.filter(test__in=tests, is_graded=True).select_related('student')

        avg_grade = submissions.aggregate(avg=Avg('grade'))['avg'] or 0
        subject_averages.append((subject.name, round(avg_grade, 2)))
        subject_chart_data[subject.name] = round(avg_grade, 2)

        # Top 10 students in this subject by average grade
        student_scores = {}
        for sub in submissions:
            student = sub.student
            student_scores.setdefault(student.username, []).append(sub.grade)

        top_students = sorted(
            [(student, sum(scores)/len(scores)) for student, scores in student_scores.items()],
            key=lambda x: x[1], reverse=True
        )[:10]

        top_students_by_subject[subject.name] = [(s[0], round(s[1], 2)) for s in top_students]

    context = {
        'subject_averages': subject_averages,
        'subject_chart_data': subject_chart_data,
        'top_students_by_subject': top_students_by_subject,
    }

    return render(request, 'analytics/teacher_analytics.html', context)


##Discussions 
@login_required
def subject_threads(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    threads = subject.threads.order_by('-created_at')
    return render(request, 'discussions/subject_threads.html', {'subject': subject, 'threads': threads})

@login_required
def create_thread(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = DiscussionThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.subject = subject
            thread.created_by = request.user
            thread.save()
            return redirect('view_thread', thread.id)
    else:
        form = DiscussionThreadForm()
    return render(request, 'discussions/create_thread.html', {'form': form, 'subject': subject})

@login_required
def view_thread(request, thread_id):
    thread = get_object_or_404(DiscussionThread, id=thread_id)
    messages = thread.messages.order_by('created_at')

    if request.method == 'POST':
        form = DiscussionMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.posted_by = request.user
            message.save()
            return redirect('view_thread', thread.id)
    else:
        form = DiscussionMessageForm()

    return render(request, 'discussions/view_thread.html', {
        'thread': thread,
        'messages': messages,
        'form': form
    })

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(DiscussionMessage, id=message_id)

    if request.user != message.posted_by:
        return HttpResponseForbidden("You can only edit your own messages.")

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, "Message updated.")
            return redirect('view_thread', thread_id=message.thread.id)
    else:
        form = MessageForm(instance=message)

    return render(request, 'discussions/edit_message.html', {'form': form, 'message': message})


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(DiscussionMessage, id=message_id)

    if request.user != message.posted_by:
        return HttpResponseForbidden("You can only delete your own messages.")

    thread_id = message.thread.id
    message.delete()
    messages.success(request, "Message deleted.")
    return redirect('view_thread', thread_id=thread_id)


#Reactions
@login_required
@require_POST
def toggle_reaction(request, message_id):
    reaction_type = request.POST.get('reaction_type')
    message = get_object_or_404(DiscussionMessage, id=message_id)

    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        message=message,
        reaction_type=reaction_type,
    )

    if not created:
        reaction.delete()
        action = 'removed'
    else:
        action = 'added'

    count = Reaction.objects.filter(message=message, reaction_type=reaction_type).count()

    return JsonResponse({'status': 'ok', 'action': action, 'count': count})


#Assignments
@login_required
def create_assignment(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.user.role != 'teacher' or request.user not in subject.teachers.all():
        return redirect('dashboard')

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.subject = subject
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('subject_detail', subject_id=subject.id)
    else:
        form = AssignmentForm()

    return render(request, 'assignments/create_assignment.html', {
        'form': form,
        'subject': subject
    })

@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user != assignment.created_by:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('subject_detail', subject_id=assignment.subject.id)
    else:
        form = AssignmentForm(instance=assignment)

    return render(request, 'assignments/edit_assignment.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def view_assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user != assignment.created_by:
        return redirect('dashboard')

    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    return render(request, 'assignments/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions
    })

@login_required
def download_all_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user != assignment.created_by:
        return redirect('dashboard')

    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for sub in submissions:
            if sub.submission_file:
                original_name = sub.submission_file.name.split('/')[-1]
                username = sub.student.username
                new_name = f"{username}_{original_name}"
                zip_file.writestr(new_name, sub.submission_file.read())
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{assignment.title}_submissions.zip"'
    return response

@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    if request.user != submission.assignment.created_by:
        return redirect('dashboard')

    if request.method == 'POST':
        grade = request.POST.get('grade')
        if grade:
            submission.grade = grade
            submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, 'Submission graded successfully.')
            return redirect('view_assignment_submissions', assignment_id=submission.assignment.id)

    return render(request, 'assignments/grade_submission.html', {
        'submission': submission
    })


@login_required
def teacher_assignment_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    # Only allow teachers assigned to this subject
    if request.user.role != 'teacher' or request.user not in subject.teachers.all():
        messages.error(request, "Access Denied.")
        return redirect('dashboard')

    assignments = Assignment.objects.filter(subject=subject).order_by('-due_date')
    return render(request, 'assignments/teacher_assignment_list.html', {
        'subject': subject,
        'assignments': assignments,
    })

@login_required
def edit_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, student=request.user)
    if timezone.now() > submission.assignment.due_date:
        messages.error(request, "Deadline passed. You can't edit this submission.")
        return redirect('submit_assignment', assignment_id=submission.assignment.id)

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Submission updated.")
            return redirect('submit_assignment', assignment_id=submission.assignment.id)
    else:
        form = AssignmentSubmissionForm(instance=submission)
    return render(request, 'assignments/edit_submission.html', {'form': form, 'submission': submission})

@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, student=request.user)
    assignment_id = submission.assignment.id
    if timezone.now() > submission.assignment.due_date:
        messages.error(request, "Deadline passed. You can't delete this submission.")
        return redirect('submit_assignment', assignment_id=assignment_id)
    
    submission.delete()
    messages.success(request, "Submission deleted.")
    return redirect('submit_assignment', assignment_id=assignment_id)

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    subject_id = assignment.subject.id
    if request.user.role != 'teacher' or request.user not in assignment.subject.teachers.all():
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Assignment deleted.")
        return redirect('teacher_assignment_list', subject_id=subject_id)
    return render(request, 'assignments/confirm_delete.html', {'assignment': assignment})

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    subject_id = assignment.subject.id
    if request.user.role != 'teacher' or request.user not in assignment.subject.teachers.all():
        messages.error(request, "Access Denied.")
        return redirect('dashboard')
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Assignment deleted.")
        return redirect('teacher_assignment_list', subject_id=subject_id)
    return render(request, 'assignments/confirm_delete.html', {'assignment': assignment})

#ss
@login_required
def student_assignment_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.user.role != 'student':
        return redirect('dashboard')

    assignments = Assignment.objects.filter(subject=subject).order_by('-due_date')
    from django.utils import timezone
    now = timezone.now()
    return render(request, 'assignments/assignment_list.html', {
        'subject': subject,
        'assignments': assignments,
        'now': now  # Pass current time to template
    })

    

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user.role != 'student':
        return redirect('dashboard')

    # Prevent submission after due date
    if timezone.now() > assignment.due_date:
        messages.warning(request, "Submission deadline has passed.")
        return redirect('student_assignment_list', subject_id=assignment.subject.id)

    # Get existing submission if any
    existing = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()
    now = timezone.now()
    assignment_closed = now > assignment.due_date
    time_left = (assignment.due_date - now).total_seconds() if not assignment_closed else 0

    if request.method == 'POST':
        if assignment_closed:
            messages.error(request, "Assignment closed. You cannot submit after the deadline.")
            return redirect('submit_assignment', assignment_id=assignment.id)
        if existing:
            messages.warning(request, "You have already submitted this assignment.")
            return redirect('submit_assignment', assignment_id=assignment.id)
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Assignment submitted successfully.")
            return redirect('submit_assignment', assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm()

    # Check if editing/deleting is allowed
    can_edit = existing and now <= assignment.due_date

    return render(request, 'assignments/submit_assignment.html', {
        'form': form,
        'assignment': assignment,
        'submission': existing,
        'can_edit': can_edit,
        'assignment_closed': assignment_closed,
        'time_left': int(time_left),
    })


#General users 
@login_required
def general_dashboard(request):
    if request.user.role != 'general':
        return redirect('dashboard')  # Redirect to internal dashboard
    return render(request, 'users/general_dashboard.html')

def general_register(request):
    if request.method == 'POST':
        form = GeneralUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_welcome_email(user)
            messages.success(request, "Account created! Please login.")
            return redirect('login')
    else:
        form = GeneralUserRegistrationForm()
    return render(request, 'users/general_register.html', {'form': form})



###Socials posts reactions ect...
@login_required
def post_feed(request):
    posts = Post.objects.prefetch_related('reactions', 'comments__user').annotate(
        total_likes=Count('reactions')
    ).order_by('-created_at')

    # Exclude current user and users already followed
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    suggestions = User.objects.exclude(id__in=following_ids).exclude(id=request.user.id)

    # Randomize and limit to 5
    suggestions = list(suggestions)
    random.shuffle(suggestions)
    suggestions = suggestions[:5]

    return render(request, 'social/post_feed.html', {
        'posts': posts,
        'suggestions': suggestions  # <-- use 'suggestions' here
    })



    
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # or post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'social/create_post.html', {'form': form})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent__isnull=True).select_related('user').prefetch_related('replies')
    form = CommentForm()
    return render(request, 'social/post_detail.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post

            parent_id = request.POST.get('parent')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()

            # Notify post owner (not the commenter themselves)
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    post=post,
                    verb="commented"
                )

            return redirect('post_feed')  # or 'post_detail' if you prefer
    return redirect('post_feed')



@login_required
@require_POST
def add_reaction(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user already liked this post
    existing_reaction = ReactionP.objects.filter(user=request.user, post=post).first()
    
    if existing_reaction:
        # Unlike the post
        existing_reaction.delete()
        action = "removed"
        liked = False
    else:
        # Like the post
        ReactionP.objects.create(user=request.user, post=post)
        action = "added"
        liked = True
        
        # Send notification (only when liking, not unliking)
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                post=post,
                verb="liked your post"
            )

    # Get updated like count
    like_count = ReactionP.objects.filter(post=post).count()

    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'liked': liked,
            'like_count': like_count
        })
    
    # Fallback for non-AJAX requests
    return redirect('post_feed')


@login_required
def notifications(request):
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    # Get all notifications for the user
    all_notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('actor', 'post').order_by('-created_at')
    
    # Group notifications by post and verb
    grouped_notifications = defaultdict(lambda: defaultdict(list))
    standalone_notifications = []
    
    for notif in all_notifications:
        if notif.post:
            # Group by post and verb type
            key = f"{notif.post.id}_{notif.verb}"
            grouped_notifications[notif.post][notif.verb].append(notif)
        else:
            # Standalone notifications (like follows)
            standalone_notifications.append(notif)
    
    # Process grouped notifications
    processed_groups = []
    for post, verb_groups in grouped_notifications.items():
        for verb, notifications in verb_groups.items():
            if len(notifications) > 1:
                # Multiple notifications of same type for same post
                latest_notif = notifications[0]  # Most recent
                actors = [n.actor for n in notifications[:5]]  # Show max 5 actors
                count = len(notifications)
                
                processed_groups.append({
                    'type': 'grouped',
                    'verb': verb,
                    'post': post,
                    'actors': actors,
                    'count': count,
                    'latest_time': latest_notif.created_at,
                    'has_more': count > 5
                })
            else:
                # Single notification
                notif = notifications[0]
                processed_groups.append({
                    'type': 'single',
                    'notification': notif,
                    'latest_time': notif.created_at
                })
    
    # Combine and sort by latest time
    all_processed = processed_groups + [
        {
            'type': 'standalone',
            'notification': notif,
            'latest_time': notif.created_at
        } for notif in standalone_notifications
    ]
    
    all_processed.sort(key=lambda x: x['latest_time'], reverse=True)
    
    # Mark today vs earlier
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    for item in all_processed:
        notif_date = item['latest_time'].date()
        if notif_date == today:
            item['time_group'] = 'today'
        elif notif_date == yesterday:
            item['time_group'] = 'yesterday'
        else:
            item['time_group'] = 'earlier'
    
    # Group by time periods
    notifications_by_time = {
        'today': [n for n in all_processed if n['time_group'] == 'today'],
        'yesterday': [n for n in all_processed if n['time_group'] == 'yesterday'],
        'earlier': [n for n in all_processed if n['time_group'] == 'earlier']
    }
    
    # Count unread (assuming you add an 'is_read' field later)
    unread_count = all_notifications.count()  # For now, count all
    
    context = {
        'notifications_by_time': notifications_by_time,
        'unread_count': unread_count,
        'has_notifications': bool(all_processed)
    }
    
    return render(request, 'social/notifications.html', context)

    

@login_required
@require_POST
def react_to_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user already liked this comment
    existing_reaction = CommentReaction.objects.filter(user=request.user, comment=comment).first()
    
    if existing_reaction:
        # Unlike the comment
        existing_reaction.delete()
        action = "removed"
        liked = False
    else:
        # Like the comment
        CommentReaction.objects.create(user=request.user, comment=comment)
        action = "added"
        liked = True
        
        # Send notification to comment author (only when liking, not unliking)
        if comment.user != request.user:
            Notification.objects.create(
                recipient=comment.user,
                actor=request.user,
                post=comment.post,
                verb="liked your comment"
            )

    # Get updated like count
    like_count = CommentReaction.objects.filter(comment=comment).count()

    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'liked': liked,
            'like_count': like_count
        })
    
    # Fallback for non-AJAX requests
    return redirect('post_detail', post_id=comment.post.id)




@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Get all top-level comments (no parent) with their replies
    comments = Comment.objects.filter(
        post=post, 
        parent=None
    ).select_related('user', 'user__profile').prefetch_related(
        'replies', 
        'replies__user', 
        'replies__user__profile'
    ).order_by('-created_at')
    
    # Form for adding new comments
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            
            # Handle parent comment for replies
            parent_id = request.POST.get('parent')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                    
                    # Send notification to parent comment author
                    if parent_comment.user != request.user:
                        Notification.objects.create(
                            recipient=parent_comment.user,
                            actor=request.user,
                            post=post,
                            verb="replied to your comment"
                        )
                except Comment.DoesNotExist:
                    pass
            else:
                # Send notification to post author for top-level comments
                if post.author != request.user:
                    Notification.objects.create(
                        recipient=post.author,
                        actor=request.user,
                        post=post,
                        verb="commented on your post"
                    )
            
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    # Get related posts from the same author
    related_posts = Post.objects.filter(
        author=post.author
    ).exclude(id=post.id).order_by('-created_at')[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'related_posts': related_posts,
    }
    
    return render(request, 'social/post_detail.html', context)


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'social/my_posts.html', {'posts': posts})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('my_posts')
    else:
        form = PostForm(instance=post)
    return render(request, 'social/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('my_posts')
    return render(request, 'social/confirm_delete_post.html', {'post': post})


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'social/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    if request.method == 'POST':
        comment.delete()
        return redirect('post_detail', post_id=post_id)
    return render(request, 'social/confirm_delete_comment.html', {'comment': comment})



@login_required
def view_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    followers_count = Follow.objects.filter(following=request.user).count()
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'social/profile.html', {
        'profile': profile,
        'followers_count': followers_count,
        'posts': posts
    })


@login_required
def edit_profile(request):
    # Ensure the user has a profile; create if missing
    try:
        profile = request.user.profile
    except AttributeError:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)
    except UserProfile.DoesNotExist:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)
    from .forms import UserAccountProfileForm
    if request.method == 'POST':
        form = UserAccountProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            # If password was changed, update session
            if form.cleaned_data.get('password'):
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
            return redirect('view_profile')
    else:
        form = UserAccountProfileForm(instance=profile, user=request.user)
    return render(request, 'social/edit_profile.html', {'form': form})



#Following
@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user != request.user:
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if created:
            # Send notification when following
            Notification.objects.create(
                recipient=target_user,
                actor=request.user,
                verb="followed you"
            )
            messages.success(request, f"You are now following {target_user.username}")
        else:
            messages.info(request, f"You are already following {target_user.username}")
    return redirect('all_users')  # Redirect back to all users page

@login_required
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    deleted_count, _ = Follow.objects.filter(follower=request.user, following=target_user).delete()
    if deleted_count > 0:
        messages.success(request, f"You have unfollowed {target_user.username}")
    else:
        messages.info(request, f"You were not following {target_user.username}")
    return redirect('all_users')  # Redirect back to all users page



@login_required
def user_profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_profile).order_by('-created_at')

    is_following = Follow.objects.filter(follower=request.user, following=user_profile).exists()
    followers_count = Follow.objects.filter(following=user_profile).count()
    following_count = Follow.objects.filter(follower=user_profile).count()

    context = {
        'user_profile': user_profile,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count
    }
    return render(request, 'social/user_profile.html', context)

from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect('user_profile', username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if created:
        # Send notification only when following
        Notification.objects.create(
            recipient=target_user,
            actor=request.user,
            verb="followed you"
        )
    else:
        follow.delete()
    return redirect('user_profile', username=username)



@login_required
def all_users(request):
    # Exclude current user, superusers, and admin role users
    users = User.objects.exclude(id=request.user.id).exclude(
        Q(is_superuser=True) | Q(role='admin')
    )
    
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    return render(request, 'social/all_users.html', {
        'users': users,
        'following_ids': set(following_ids)
    })



#Labb
@login_required
def draft_list(request):
    drafts = DraftingSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'lab/draft_list.html', {'drafts': drafts})

@login_required
def create_draft(request):
    if request.method == 'POST':
        form = DraftingSessionForm(request.POST, request.FILES)
        if form.is_valid():
            draft = form.save(commit=False)
            draft.user = request.user
            draft.save()
            return redirect('draft_workspace', pk=draft.pk)
    else:
        form = DraftingSessionForm()
    return render(request, 'lab/create_draft.html', {'form': form})




@login_required
def draft_workspace(request, pk):
    draft = get_object_or_404(DraftingSession, pk=pk, user=request.user)
    pages = draft.pages.all()
    page_images = {page.page_number: page.image.url for page in pages if page.image}
    return render(request, 'lab/draft_workspace.html', {
        'session': draft,
        'page_images': page_images,
        'max_pages': 5,
    })

    
@login_required
@csrf_exempt
def save_canvas_image(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(DraftingSession, id=session_id, user=request.user)
        import json
        data = json.loads(request.body)
        image_data = data.get('image_data')
        page_number = int(data.get('page_number', 1))

        if image_data and 1 <= page_number <= 5:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f'canvas_{session_id}_page{page_number}.{ext}'
            page, _ = CanvasPage.objects.get_or_create(draft=session, page_number=page_number)
            page.image.save(file_name, ContentFile(base64.b64decode(imgstr)))
            page.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

    
@login_required
def delete_draft(request, pk):
    draft = get_object_or_404(DraftingSession, pk=pk, user=request.user)
    draft.delete()
    return redirect('draft_list')


@xframe_options_exempt
def serve_pdf(request, session_id):
    try:
        session = DraftingSession.objects.get(id=session_id, user=request.user)
        file_path = session.pdf_file.path
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except DraftingSession.DoesNotExist:
        raise Http404("PDF not found")
    except Exception as e:
        raise Http404(f"Error: {e}")


import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt




###

def recover_username(request):
    if request.method == 'POST':
        form = UsernameRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_mail(
                    subject='LMS - Username Recovery',
                    message=f'Hi {user.first_name},\n\nYour username is: {user.username}\n\nRegards,\nLMS Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "✅ Your username was sent to your email.")
            except User.DoesNotExist:
                messages.error(request, "❌ No account found with that email.")
            except Exception as e:
                messages.error(request, f"❌ Error sending email: {e}")
    else:
        form = UsernameRecoveryForm()

    return render(request, 'accounts/recover_username.html', {'form': form})


def test_email(request):
    try:
        # Create secure context using certifi's trusted CA bundle
        secure_context = ssl.create_default_context(cafile=certifi.where())

        # Manually open a verified SMTP connection
        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username='m48209921@gmail.com',
            password='ilyu emhb tnuo ayur',  # ← Use App Password if Gmail has 2FA
            use_tls=True,
            fail_silently=False,
        )

        # Inject certifi’s SSL context into Django's SMTP session
        connection.connection.starttls(context=secure_context)

        # Send the test email
        send_mail(
            'Test Subject',
            'This is a test message from your Django app.',
            'm48209921@gmail.com',
            ['mthunziapplications@example.com'],  # ← Replace with real recipient
            connection=connection,
        )

        return HttpResponse("✅ Email sent successfully!")

    except Exception as e:
        return HttpResponse(f"❌ Failed to send email: {str(e)}")













def recover_username(request):
    if request.method == 'POST':
        form = UsernameRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_mail(
                    subject='LMS - Username Recovery',
                    message=f'Hi {user.first_name or user.username},\n\nYour username is: {user.username}\n\nRegards,\nGlobalFuture Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "✅ Your username was sent to your email.")
            except User.DoesNotExist:
                messages.error(request, "❌ No account found with that email.")
            except Exception as e:
                messages.error(request, f"❌ Error sending email: {e}")
    else:
        form = UsernameRecoveryForm()
    return render(request, 'accounts/recover_username.html', {'form': form})





##Conversions
def convert_document(request):
    converted_file_url = None
    ocr_text = None

    if request.method == 'POST':
        form = DocumentConversionForm(request.POST, request.FILES)
        if form.is_valid():
            conversion_type = form.cleaned_data['conversion_type']
            uploaded_file = request.FILES['file']
            user = request.user

            # Save original file
            doc_conv = DocumentConversion.objects.create(
                user=user,
                original_file=uploaded_file,
                conversion_type=conversion_type
            )
            input_path = doc_conv.original_file.path

            if conversion_type == 'pdf2docx':
                output_path = input_path.replace('.pdf', '.docx')
                cv = Converter(input_path)
                cv.convert(output_path, start=0, end=None)
                cv.close()
                with open(output_path, 'rb') as f:
                    doc_conv.converted_file.save(os.path.basename(output_path), ContentFile(f.read()))
                converted_file_url = doc_conv.converted_file.url

            elif conversion_type == 'docx2pdf':
                output_path = input_path.replace('.docx', '.pdf')
                docx2pdf_convert(input_path, output_path)
                with open(output_path, 'rb') as f:
                    doc_conv.converted_file.save(os.path.basename(output_path), ContentFile(f.read()))
                converted_file_url = doc_conv.converted_file.url

            elif conversion_type == 'pdf2ocr':
                images = convert_from_path(input_path)
                text = ""
                for img in images:
                    text += pytesseract.image_to_string(img)
                ocr_text = text

            doc_conv.save()
    else:
        form = DocumentConversionForm()

    return render(request, 'lab/convert_document.html', {
        'form': form,
        'converted_file_url': converted_file_url,
        'ocr_text': ocr_text,
    })




def custom_login(request):
    from django.template.context_processors import csrf
    context = {}
    context.update(csrf(request))
    # If user is already authenticated, go to dashboard
    if request.user.is_authenticated:
        # Use the same dashboard logic for redirect
        user = request.user
        if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
            return redirect('dashboard')
        elif hasattr(user, 'role'):
            if user.role == 'school_admin':
                return redirect('dashboard')
            elif user.role == 'teacher':
                return redirect('dashboard')
            elif user.role == 'student':
                return redirect('dashboard')
            elif user.role == 'general':
                return redirect('dashboard')
            else:
                return redirect('/accounts/login/')
        else:
            return redirect('/accounts/login/')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            # After login, use the same dashboard logic for redirect
            user = form.get_user()
            if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
                return redirect('dashboard')
            elif hasattr(user, 'role'):
                if user.role == 'school_admin':
                    return redirect('dashboard')
                elif user.role == 'teacher':
                    return redirect('dashboard')
                elif user.role == 'student':
                    return redirect('dashboard')
                elif user.role == 'general':
                    return redirect('dashboard')
                else:
                    return redirect('/accounts/login/')
            else:
                return redirect('/accounts/login/')
    else:
        form = AuthenticationForm()
    # Social providers for template
    providers = []
    try:
        provider_list = registry.get_list()
    except AttributeError:
        provider_list = []
    for provider in provider_list:
        try:
            SocialApp.objects.get(provider=provider.id, sites=settings.SITE_ID)
            providers.append(provider)
        except SocialApp.DoesNotExist:
            pass
    context['form'] = form
    context['socialaccount_providers'] = providers
    # Add extra options for template customization
    context['show_register'] = True
    context['show_forgot_password'] = True
    context['show_forgot_username'] = True
    return render(request, 'registration/login.html', context)

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'admin')

def is_school_admin(user):
    return hasattr(user, 'role') and user.role == 'school_admin'

@user_passes_test(is_admin)
def send_email_to_all_users(request):
    from .models import User
    from django.core.mail import send_mail
    if request.method == 'POST':
        form = BulkEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipient_list = list(User.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
            send_mail(subject, message, request.user.email or 'admin@global-lms.com', recipient_list, fail_silently=False)
            messages.success(request, f"Email sent to {len(recipient_list)} users.")
            return redirect('dashboard')
    else:
        form = BulkEmailForm()
    return render(request, 'admin_send_email.html', {'form': form})

@user_passes_test(is_school_admin)
def send_email_to_school_students(request):
    from .models import User
    from django.core.mail import send_mail
    school_id = request.user.school_id
    if request.method == 'POST':
        form = BulkEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipient_list = list(User.objects.filter(role='student', school_id=school_id).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
            send_mail(subject, message, request.user.email or 'schooladmin@global-lms.com', recipient_list, fail_silently=False)
            messages.success(request, f"Email sent to {len(recipient_list)} students.")
            return redirect('dashboard')
    else:
        form = BulkEmailForm()
    return render(request, 'school_send_email.html', {'form': form})





def global_search(request):
    query = request.GET.get('q', '').strip()
    posts = []
    users = []
    if query:
        posts = Post.objects.filter(
            Q(content__icontains=query)
        )
        User = get_user_model()
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    return render(request, 'global_search.html', {
        'query': query,
        'posts': posts,
        'users': users,
    })