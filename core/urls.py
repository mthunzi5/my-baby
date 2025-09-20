from . import views_colledge_test_submissions
from . import views_colledge_assignment_submissions
from . import views_colledge_test_take
from . import views_colledge_test_questions
from . import views_colledge_assignment_submit
from . import views_colledge_subject_test
from . import views_colledge_subject_assignment
   
from . import views_colledge_subject_file
from . import views_colledge_subject
from . import views_colledge_admin
    
from . import views_colledge_my
from . import views_colledge_dashboard
from . import views_colledge_payment
from . import views_colledge_notify
from . import views_colledge
   
from django.urls import path, include
from . import views
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from .views import send_email_to_all_users, send_email_to_school_students

urlpatterns = [
    path('', views.custom_login, name='custom_login'),  # Use custom login as landing page
    path('login/', views.custom_login, name='login'),  # Add this for Django's auth views and templates
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-school-admin/', views.create_school_admin, name='create_school_admin'),
    path('school-admins/', views.list_school_admins, name='list_school_admins'),
    path('school-admins/edit/<int:user_id>/', views.edit_school_admin, name='edit_school_admin'),
    path('school-admins/delete/<int:user_id>/', views.delete_school_admin, name='delete_school_admin'),
    path('logout/', LogoutView.as_view(next_page='custom_login'), name='logout'),
    path('school-users/', views.list_school_users, name='list_school_users'),
    path('school-users/create/', views.create_school_user, name='create_school_user'),
    path('school-users/edit/<int:user_id>/', views.edit_school_user, name='edit_school_user'),
    path('school-users/delete/<int:user_id>/', views.delete_school_user, name='delete_school_user'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:subject_id>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    path('subjects/<int:subject_id>/manage/', views.subject_manage_users, name='subject_manage_users'),
    path('my-subjects/', views.my_subjects, name='my_subjects'),

    path('files/upload/', views.upload_subject_file, name='upload_subject_file'),
    path('files/my/', views.my_subject_files, name='my_subject_files'),
    path('subject/<int:subject_id>/files/', views.view_subject_files, name='view_subject_files'),

    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/upload/', views.upload_subject_file, name='upload_subject_file'),
    path('subject/<int:subject_id>/delete_file/<int:file_id>/', views.delete_subject_file, name='delete_subject_file'),

    # -------- TEACHER Test Management --------
    path('subjects/<int:subject_id>/tests/', views.subject_tests, name='subject_tests'),
    path('subjects/<int:subject_id>/tests/create/', views.create_test, name='create_test'),
    path('tests/<int:test_id>/questions/add/', views.add_questions, name='add_questions'),
    path('tests/<int:test_id>/post/', views.post_test, name='post_test'),
    path('tests/<int:test_id>/open/', views.open_test, name='open_test'),
    path('tests/<int:test_id>/close/', views.close_test, name='close_test'),

    # -------- STUDENT Test Interaction --------
    path('tests/<int:test_id>/write/', views.write_test, name='write_test'),
    path('my_tests/', views.my_tests, name='my_tests'),

    # -------- Teacher View + Grading Submissions --------
    path('tests/<int:test_id>/submissions/', views.view_test_submissions, name='view_test_submissions'),
    path('submissions/<int:submission_id>/manual-grade/', views.manual_grade, name='manual_grade'),
    path('tests/<int:test_id>/grade_all/', views.grade_all_auto, name='grade_all_auto'),

    # Analytics 
    path('analytics/student/', views.student_analytics, name='student_analytics'),
    path('analytics/teacher/', views.teacher_analytics, name='teacher_analytics'),

    # Discussion / Forum URLs
    path('subjects/<int:subject_id>/threads/', views.subject_threads, name='subject_threads'),
    path('subjects/<int:subject_id>/threads/create/', views.create_thread, name='create_thread'),
    path('threads/<int:thread_id>/', views.view_thread, name='view_thread'),
    path('discussions/message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('discussions/message/<int:message_id>/delete/', views.delete_message, name='delete_message'),

    # React
    path('discussion/message/<int:message_id>/react/', views.toggle_reaction, name='toggle_reaction'),

    # Assignments
    # Teacher: Create & Manage Assignments
    path('subjects/<int:subject_id>/assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),

    # Student: View Assignments
    path('subjects/<int:subject_id>/assignments/', views.student_assignment_list, name='student_assignment_list'),

    # Teacher: View Assignments (separate URL or template for teachers)
    path('subjects/<int:subject_id>/teacher-assignments/', views.teacher_assignment_list, name='teacher_assignment_list'),

    # Student: Submit Assignment
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    
    # Teacher: View Assignment Submissions
    path('assignments/<int:assignment_id>/submissions/', views.view_assignment_submissions, name='view_assignment_submissions'),
    # urls.py
    path('assignments/<int:assignment_id>/download_all/', views.download_all_submissions, name='download_all_submissions'),
    # Teacher: Grade Individual Assignment Submission
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),

    path('submission/<int:submission_id>/edit/', views.edit_submission, name='edit_submission'),
    path('submission/<int:submission_id>/delete/', views.delete_submission, name='delete_submission'),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    
    #General users 
    path('register/', views.general_register, name='general_register'),
    path('general/dashboard/', views.general_dashboard, name='general_dashboard'),

    ###
    path('feed/', views.post_feed, name='post_feed'),
    path('feed/create/', views.create_post, name='create_post'),
    path('feed/<int:post_id>/', views.post_detail, name='post_detail'),
    path('feed/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('feed/<int:post_id>/react/', views.add_reaction, name='add_reaction'),
    path('notifications/', views.notifications, name='notifications'),
    path('feed/', views.post_feed, name='feed'),
    path('feed/create/', views.create_post, name='create_post'),
    path('notifications/', views.notifications, name='notifications'),

    path('feed/', views.post_feed, name='post_feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.add_reaction, name='add_reaction'),
    path('comment/<int:comment_id>/react/', views.react_to_comment, name='react_to_comment'),
    path('notifications/', views.notifications, name='notifications'),
    path('comment/<int:comment_id>/react/', views.react_to_comment, name='react_to_comment'),

    path('social/react/<int:post_id>/', views.add_reaction, name='add_reaction'),

    # Example for urls.py
    path('my_posts/', views.my_posts, name='my_posts'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    ##Followers
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('users/', views.all_users, name='all_users'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('toggle_follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('drafts/<int:session_id>/pdf/', views.serve_pdf, name='serve_pdf'),
    path('drafts/<int:pk>/save/', views.save_canvas_image, name='save_canvas_image'),

    #LAB 
   
    #Lab 2
    path('drafts/', views.draft_list, name='draft_list'),
    path('drafts/create/', views.create_draft, name='create_draft'),
    path('drafts/<int:pk>/', views.draft_workspace, name='draft_workspace'),
    path('drafts/<int:pk>/save/', views.save_canvas_image, name='save_canvas_image'),
    path('drafts/<int:pk>/delete/', views.delete_draft, name='delete_draft'),

    path('drafts/<int:session_id>/save-canvas/', views.save_canvas_image, name='save_canvas_image'),

    ##PasswordRecovery
    path('forgot-password/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('recover-username/', views.recover_username, name='recover_username'),
    path('test-email/', views.test_email, name='test_email'),





    path('accounts/recover-username/', views.recover_username, name='recover_username'),


    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    #Conversions
    path('lab/convert/', views.convert_document, name='convert_document'),

    path('colledge/create/', views_colledge.create_colledge_class, name='create_colledge_class'),

    path('colledge/<int:colledge_id>/payment/', views_colledge_payment.payfast_payment, name='payfast_payment'),
    path('colledge/<int:colledge_id>/payment/success/', views_colledge_notify.payfast_success, name='payfast_success'),
    path('colledge/<int:colledge_id>/payment/cancel/', views_colledge_notify.payfast_cancel, name='payfast_cancel'),
    path('colledge/<int:colledge_id>/payment/notify/', views_colledge_notify.payfast_notify, name='payfast_notify'),
    path('colledge/<int:colledge_id>/', views_colledge_dashboard.colledge_dashboard, name='colledge_dashboard'),
    path('colledge/my/', views_colledge_my.my_colledge_classes, name='my_colledge_classes'),

    path('colledge/admin/list/', views_colledge_admin.admin_colledge_list, name='admin_colledge_list'),
    path('colledge/<int:colledge_id>/delete/', views_colledge_admin.delete_colledge_class, name='delete_colledge_class'),
    path('colledge/<int:colledge_id>/subjects/', views_colledge_subject.colledge_subjects, name='colledge_subjects'),
    path('colledge/subject/<int:subject_id>/files/', views_colledge_subject_file.colledge_subject_files, name='colledge_subject_files'),
    path('colledge/subject/<int:subject_id>/tests/', views_colledge_subject_test.colledge_subject_tests, name='colledge_subject_tests'),
    path('colledge/subject/<int:subject_id>/assignments/', views_colledge_subject_assignment.colledge_subject_assignments, name='colledge_subject_assignments'),
    path('colledge/test/<int:test_id>/questions/', views_colledge_test_questions.colledge_test_questions, name='colledge_test_questions'),
    path('colledge/assignment/<int:assignment_id>/submit/', views_colledge_assignment_submit.colledge_assignment_submit, name='colledge_assignment_submit'),
    path('colledge/test/<int:test_id>/take/', views_colledge_test_take.colledge_test_take, name='colledge_test_take'),
    path('colledge/test/<int:test_id>/submissions/', views_colledge_test_submissions.colledge_test_submissions, name='colledge_test_submissions'),
    path('colledge/assignment/<int:assignment_id>/submissions/', views_colledge_assignment_submissions.colledge_assignment_submissions, name='colledge_assignment_submissions'),
     # Colledge test open/close
    path('colledge/test/<int:test_id>/open/', views_colledge_subject_test.colledge_test_open, name='colledge_test_open'),
    path('colledge/test/<int:test_id>/close/', views_colledge_subject_test.colledge_test_close, name='colledge_test_close'),
    path('colledge/history/', views_colledge_my.my_colledge_history, name='my_colledge_history'),
    path('colledge/history/', views_colledge_dashboard.my_colledge_history, name='my_colledge_history'),


    path('search/', views.global_search, name='global_search'),


    

  





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('email/all/', send_email_to_all_users, name='admin_send_email'),
    path('school/send-email/', send_email_to_school_students, name='school_send_email'),
]