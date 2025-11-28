from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),                  
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contribute/', views.contribute, name='contribute'),
    path('documentation/', views.documentation, name='documentation'),
    path('team/', views.team, name='team'),
    path('data-license/', views.data_license, name='data_license'),
    path('contributor-agreement/', views.contributor_agreement, name='contributor_agreement'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Bulk upload (CSV)
    #path('upload/', views.bulk_upload, name='bulk_upload'),

    # Example dynamic paths
    # path('plants/<int:plant_id>/', views.plant_detail, name='plant_detail'),
    # path('compounds/<int:compound_id>/', views.compound_detail, name='compound_detail'),
]
