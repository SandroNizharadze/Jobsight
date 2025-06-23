from core.views.employer_views.dashboard import employer_dashboard, employer_home
from core.views.employer_views.job_management import post_job, delete_job, extend_job, restore_job, deleted_jobs
from core.views.employer_views.application_management import job_applications, update_application_status, application_detail
from core.views.employer_views.cv_database import cv_database
from core.views.employer_views.profile import company_profile, get_job_details

# For backward compatibility, expose all views at the module level
__all__ = [
    'employer_dashboard', 'employer_home',
    'post_job', 'delete_job', 'extend_job', 'restore_job', 'deleted_jobs',
    'job_applications', 'update_application_status', 'application_detail',
    'cv_database',
    'company_profile', 'get_job_details',
] 