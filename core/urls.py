from django.urls import path
from .views import main, auth_views, job_views, employer_views, profile_views, admin_views
from .views.job_views import save_job, unsave_job
from .views.file_views import serve_cv_file
from .views.profile_views import get_application_rejection_reasons, view_cv_employer, mark_candidate_notifications_as_read, mark_candidate_notification_as_read, applications, saved_jobs
from .views.employer_views import company_profile, application_detail, cv_database
from django.views.generic.base import RedirectView
from .views.blog_views import BlogListView, BlogPostDetailView, BlogCategoryView
from .views.email_views import verify_email, resend_verification_email
from .views.static_pages import StaticPageView

urlpatterns = [
    path('', job_views.job_list, name='job_list'),
    path('jobs/', RedirectView.as_view(url='/', permanent=True), name='jobs_redirect'),
    path('home/', main.home_redirect, name='home_redirect'),
    path('jobs/<int:job_id>/', job_views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', job_views.apply_job, name='apply_job'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register, name='register'),
    path('profile/', profile_views.profile, name='profile'),
    path('profile/remove-cv/', profile_views.remove_cv, name='remove_cv'),
    path('profile/delete-account/', profile_views.delete_account, name='delete_account'),
    path('profile/update-employer-profile/', profile_views.update_employer_profile, name='update_employer_profile'),
    
    # Candidate profile pages
    path('profile/applications/', applications, name='candidate_applications'),
    path('profile/saved-jobs/', saved_jobs, name='candidate_saved_jobs'),
    
    # Email verification URLs
    path('verify-email/<str:token>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    
    path('employer/', employer_views.employer_home, name='employer_home'),
    path('employer/dashboard/', employer_views.employer_dashboard, name='employer_dashboard'),
    path('employer/deleted-jobs/', employer_views.deleted_jobs, name='deleted_jobs'),
    path('employer/delete-job/<int:job_id>/', employer_views.delete_job, name='delete_job'),
    path('employer/restore-job/<int:job_id>/', employer_views.restore_job, name='restore_job'),
    path('employer/extend-job/<int:job_id>/', employer_views.extend_job, name='extend_job'),
    path('employer/job-applications/<int:job_id>/', employer_views.job_applications, name='job_applications'),
    path('employer/update-application-status/<int:application_id>/', employer_views.update_application_status, name='update_application_status'),
    path('employer/get-job-details/<int:job_id>/', employer_views.get_job_details, name='get_job_details'),
    
    # Notification routes
    path('employer/notifications/mark-all-read/', employer_views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('employer/notifications/mark-job-read/<int:job_id>/', employer_views.mark_job_notifications_as_read, name='mark_job_notifications_as_read'),
    path('employer/notifications/mark-read/<int:notification_id>/', employer_views.mark_notification_as_read, name='mark_notification_as_read'),
    
    # Candidate notification routes
    path('candidate/notifications/mark-all-read/', mark_candidate_notifications_as_read, name='mark_candidate_notifications_as_read'),
    path('candidate/notifications/mark-read/<int:notification_id>/', mark_candidate_notification_as_read, name='mark_candidate_notification_as_read'),
    
    path('admin/create/', admin_views.create_admin, name='create_admin'),
    path('admin/assign-employer/', admin_views.assign_employer, name='assign_employer'),
    path('pricing/', main.pricing, name='pricing'),
    
    # Blog URLs - SEO friendly
    path('blog/', BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', BlogPostDetailView.as_view(), name='blog_post_detail'),
    path('blog/category/<slug:slug>/', BlogCategoryView.as_view(), name='blog_category'),
    
    path('cv/view/', serve_cv_file, name='view_cv'),
    path('cv/view/<int:user_id>/', serve_cv_file, name='view_user_cv'),
    path('create-admin/<str:secret_key>/', main.create_admin, name='create_admin'),
    
    # Employer routes
    path('employer/profile/', main.employer_dashboard, name='employer_dashboard'),  # Keep old URL for backward compatibility
    path('employer/jobs/post/', employer_views.post_job, name='post_job'),
    path('employer/jobs/<int:job_id>/details/', main.get_job_details, name='get_job_details'),
    path('employer/jobs/<int:job_id>/delete/', main.delete_job, name='delete_job'),
    path('employer/jobs/<int:job_id>/restore/', main.restore_job, name='restore_job'),
    path('employer/jobs/<int:job_id>/extend/', main.extend_job, name='extend_job'),
    path('employer/home/', main.employer_home, name='employer_home'),
    path('employer/applications/<int:application_id>/', application_detail, name='application_detail'),
    path('employer/applications/<int:application_id>/update-status/', main.update_application_status, name='update_application_status'),
    path('company/<int:employer_id>/', company_profile, name='company_profile'),
    
    # CV Database routes
    path('employer/cv-database/', cv_database, name='cv_database'),
    path('employer/cv-database/view/<int:profile_id>/', view_cv_employer, name='view_cv_employer'),
    
    # Job routes
    path('jobs/<int:job_id>/save/', save_job, name='save_job'),
    path('jobs/<int:job_id>/unsave/', unsave_job, name='unsave_job'),
    
    # API routes
    path('api/applications/<int:application_id>/rejection-reasons/', get_application_rejection_reasons, name='get_application_rejection_reasons'),
    path('jobs/filter/', job_views.filter_jobs, name='filter_jobs'),
    
    # Static Pages
    path('privacy-policy/', StaticPageView.as_view(), {'page_type': 'privacy_policy'}, name='privacy_policy'),
    path('terms-and-conditions/', StaticPageView.as_view(), {'page_type': 'terms_conditions'}, name='terms_conditions'),
]