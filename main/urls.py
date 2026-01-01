from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),                  
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contribute/', views.contribute, name='contribute'),
    path('documentation/', views.documentation, name='documentation'),
    path('team/', views.team, name='team'),
    path('data-license/', views.data_license, name='data_license'),
    path('contributor-agreement/', views.contributor_agreement, name='contributor_agreement'),

    # Plants
    path('plant/<int:pk>/', views.plant_detail, name='plant_detail'),
    path('plants/<int:plant_id>/phytochemicals/export/', views.export_plant_phytochemicals_csv, name='export_plant_phytochemicals_csv'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path("contribution/<int:contrib_id>/", views.contribution_detail, name="contribution_detail"),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html', email_template_name="registration/password_reset_email.html", subject_template_name="registration/password_reset_subject.txt"), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Manager Review
    path('review-contributions/', views.review_contributions, name='review_contributions'),
    path('approve/<int:contrib_id>/', views.approve_contribution, name='approve_contribution'),
    path('reject/<int:contrib_id>/', views.reject_contribution, name='reject_contribution'),

    # Review & Approval
    path('review/', views.review_contributions, name='review_contributions'),
    path('approve/<int:contrib_id>/', views.approve_contribution, name='approve_contribution'),
    path('reject/<int:contrib_id>/', views.reject_contribution, name='reject_contribution'),

    # NVIDIA DiffDock
    path('molecular_docking/', views.docking_with_diffdock, name='docking_with_diffdock'),
    path('molecular_docking/submitted/<str:job_id>/', views.docking_submitted, name='docking_submitted'),
    path("docking/status/<uuid:job_id>/", views.docking_status, name="docking_status"),
    path("docking/results/<uuid:job_id>/", views.docking_results, name="docking_results"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)