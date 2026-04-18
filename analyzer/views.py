"""
Django views for AI Resume Intelligence Platform.
All analysis views return JSON for AJAX rendering.
"""
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .utils.pdf_parser import extract_text
from .utils.gemini_ai import analyze_resume, gap_analysis as run_gap_analysis, extract_skills
from .utils.charts import generate_radar_chart_data, generate_gauge_data
from .utils.pdf_export import generate_report_pdf
from .utils.scraper import scrape_linkedin_jobs


@ensure_csrf_cookie
def home(request):
    """Landing page. ensure_csrf_cookie sets the CSRF cookie on first visit."""
    return render(request, 'home.html')


def _extract_resume_text(request):
    """Helper: extract text from uploaded resume file."""
    resume_file = request.FILES.get('resume')
    if not resume_file:
        return None, "No resume file uploaded."

    filename = resume_file.name
    allowed_extensions = ['pdf', 'docx', 'txt']
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext not in allowed_extensions:
        return None, f"Unsupported format: .{ext}. Please upload PDF, DOCX, or TXT."

    try:
        text = extract_text(resume_file, filename)
        if not text.strip():
            return None, "Could not extract text from the file. The file may be empty or image-based."
        return text, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


@csrf_exempt
@require_http_methods(["POST"])
def analyze_summary(request):
    """Analyze resume and return summary."""
    api_key = request.POST.get('api_key', '').strip()
    if not api_key:
        return JsonResponse({'error': 'Please provide your Gemini API Key.'}, status=400)

    text, error = _extract_resume_text(request)
    if error:
        return JsonResponse({'error': error}, status=400)

    try:
        result = analyze_resume(api_key, text, 'summary')
        skills = extract_skills(api_key, text)
        radar_data = generate_radar_chart_data(skills)

        # Store in session for PDF export
        request.session['last_analysis'] = {
            'filename': request.FILES['resume'].name,
            'summary': result,
            'skills': skills,
        }

        return JsonResponse({
            'result': result,
            'radar_chart': json.loads(radar_data),
            'skills': skills,
        })
    except Exception as e:
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_strength(request):
    """Analyze resume strengths."""
    api_key = request.POST.get('api_key', '').strip()
    if not api_key:
        return JsonResponse({'error': 'Please provide your Gemini API Key.'}, status=400)

    text, error = _extract_resume_text(request)
    if error:
        return JsonResponse({'error': error}, status=400)

    try:
        result = analyze_resume(api_key, text, 'strength')

        session_data = request.session.get('last_analysis', {})
        session_data['strength'] = result
        session_data['filename'] = request.FILES['resume'].name
        request.session['last_analysis'] = session_data

        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_weakness(request):
    """Analyze resume weaknesses."""
    api_key = request.POST.get('api_key', '').strip()
    if not api_key:
        return JsonResponse({'error': 'Please provide your Gemini API Key.'}, status=400)

    text, error = _extract_resume_text(request)
    if error:
        return JsonResponse({'error': error}, status=400)

    try:
        result = analyze_resume(api_key, text, 'weakness')

        session_data = request.session.get('last_analysis', {})
        session_data['weakness'] = result
        session_data['filename'] = request.FILES['resume'].name
        request.session['last_analysis'] = session_data

        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_job_titles(request):
    """Suggest job titles based on resume."""
    api_key = request.POST.get('api_key', '').strip()
    if not api_key:
        return JsonResponse({'error': 'Please provide your Gemini API Key.'}, status=400)

    text, error = _extract_resume_text(request)
    if error:
        return JsonResponse({'error': error}, status=400)

    try:
        result = analyze_resume(api_key, text, 'job_titles')

        session_data = request.session.get('last_analysis', {})
        session_data['job_titles'] = result
        session_data['filename'] = request.FILES['resume'].name
        request.session['last_analysis'] = session_data

        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def gap_analysis(request):
    """Compare resume against a job description."""
    api_key = request.POST.get('api_key', '').strip()
    job_description = request.POST.get('job_description', '').strip()

    if not api_key:
        return JsonResponse({'error': 'Please provide your Gemini API Key.'}, status=400)
    if not job_description:
        return JsonResponse({'error': 'Please paste the job description.'}, status=400)

    text, error = _extract_resume_text(request)
    if error:
        return JsonResponse({'error': error}, status=400)

    try:
        result = run_gap_analysis(api_key, text, job_description)
        gauge_data = generate_gauge_data(result.get('match_score', 0))

        session_data = request.session.get('last_analysis', {})
        session_data['gap_analysis'] = result
        session_data['filename'] = request.FILES['resume'].name
        request.session['last_analysis'] = session_data

        return JsonResponse({
            'result': result,
            'gauge_chart': json.loads(gauge_data),
        })
    except Exception as e:
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def export_pdf(request):
    """Export analysis results as a PDF report."""
    analysis_data = request.session.get('last_analysis', {})

    if not analysis_data:
        return JsonResponse({'error': 'No analysis data found. Please run an analysis first.'}, status=400)

    try:
        pdf_buffer = generate_report_pdf(analysis_data)

        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        filename = analysis_data.get('filename', 'resume')
        response['Content-Disposition'] = f'attachment; filename="analysis_report_{filename}.pdf"'
        return response
    except Exception as e:
        return JsonResponse({'error': f'PDF generation failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def linkedin_scraper_view(request):
    """Scrape LinkedIn jobs."""
    job_title = request.POST.get('job_title', '').strip()
    job_location = request.POST.get('job_location', 'India').strip()
    job_count = int(request.POST.get('job_count', 5))

    if not job_title:
        return JsonResponse({'error': 'Please enter a job title.'}, status=400)

    job_titles = [t.strip() for t in job_title.split(',') if t.strip()]

    try:
        results = scrape_linkedin_jobs(job_titles, job_location, job_count)

        if isinstance(results, dict) and 'error' in results:
            return JsonResponse({'error': results['error']}, status=500)

        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': f'Scraping failed: {str(e)}'}, status=500)
