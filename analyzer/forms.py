"""
Django forms for the analyzer app.
"""
from django import forms


class ResumeUploadForm(forms.Form):
    """Form for uploading a resume file."""
    resume = forms.FileField(
        required=True,
        help_text='Upload your resume (PDF, DOCX, or TXT)',
    )
    api_key = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.PasswordInput(),
        help_text='Enter your Gemini API Key',
    )


class GapAnalysisForm(forms.Form):
    """Form for resume vs job description gap analysis."""
    resume = forms.FileField(
        required=True,
        help_text='Upload your resume (PDF, DOCX, or TXT)',
    )
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8}),
        required=True,
        help_text='Paste the job description here',
    )
    api_key = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.PasswordInput(),
        help_text='Enter your Gemini API Key',
    )


class LinkedInScraperForm(forms.Form):
    """Form for LinkedIn job scraping."""
    job_title = forms.CharField(
        max_length=200,
        required=True,
        help_text='Job titles (comma-separated)',
    )
    job_location = forms.CharField(
        max_length=100,
        required=True,
        initial='India',
        help_text='Job location',
    )
    job_count = forms.IntegerField(
        min_value=1,
        max_value=25,
        initial=5,
        help_text='Number of jobs to scrape',
    )
