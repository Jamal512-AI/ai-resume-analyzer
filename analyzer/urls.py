"""
URL patterns for the analyzer app.
"""
from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/summary/', views.analyze_summary, name='summary'),
    path('analyze/strength/', views.analyze_strength, name='strength'),
    path('analyze/weakness/', views.analyze_weakness, name='weakness'),
    path('analyze/job-titles/', views.analyze_job_titles, name='job_titles'),
    path('analyze/gap/', views.gap_analysis, name='gap_analysis'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('scraper/linkedin/', views.linkedin_scraper_view, name='linkedin'),
]
