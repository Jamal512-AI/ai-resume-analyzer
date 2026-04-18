/* ============================================
   AI Resume Intelligence Platform
   Main JavaScript — AJAX, UI Interactions
   ============================================ */

// ─── CSRF Token Helper ───
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// ─── Loader ───
function showLoader(message = 'Analyzing your resume with AI...') {
    const overlay = document.getElementById('loaderOverlay');
    const text = document.getElementById('loaderText');
    if (overlay) {
        text.textContent = message;
        overlay.classList.add('active');
    }
}

function hideLoader() {
    const overlay = document.getElementById('loaderOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// ─── Mobile Navigation ───
function toggleMobileNav() {
    const links = document.getElementById('navLinks');
    if (links) {
        links.classList.toggle('open');
    }
}

// ─── Tab Switching ───
function switchTab(btn, tabId) {
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    // Remove active from all tab content
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

    // Add active to clicked button and corresponding content
    btn.classList.add('active');
    const tab = document.getElementById(tabId);
    if (tab) tab.classList.add('active');

    // Hide results when switching tabs
    const results = document.getElementById('analysisResults');
    if (results) results.classList.add('hidden');
}

// ─── File Upload Handler ───
function handleFileSelect(input, zoneId) {
    const zone = document.getElementById(zoneId);
    const fileNameMap = {
        'uploadZoneSummary': 'fileNameSummary',
        'uploadZoneStrength': 'fileNameStrength',
        'uploadZoneWeakness': 'fileNameWeakness',
        'uploadZoneJobTitles': 'fileNameJobTitles',
        'uploadZoneGap': 'fileNameGap',
    };

    const fileNameEl = document.getElementById(fileNameMap[zoneId]);

    if (input.files && input.files[0]) {
        const file = input.files[0];
        if (fileNameEl) {
            fileNameEl.textContent = `✅ ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        }
        if (zone) {
            zone.style.borderColor = 'var(--accent-success)';
            zone.style.background = 'rgba(0, 230, 118, 0.03)';
        }
    }
}

// ─── Drag and Drop ───
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.upload-zone').forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            const input = zone.querySelector('input[type="file"]');
            if (input && e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                handleFileSelect(input, zone.id);
            }
        });
    });
});

// ─── Submit Resume Analysis (Summary, Strength, Weakness, Job Titles) ───
async function submitAnalysis(event, type) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const urlMap = {
        'summary': '/analyze/summary/',
        'strength': '/analyze/strength/',
        'weakness': '/analyze/weakness/',
        'job-titles': '/analyze/job-titles/',
    };

    const loaderMessages = {
        'summary': '📝 Generating resume summary...',
        'strength': '💪 Analyzing your strengths...',
        'weakness': '🎯 Identifying areas for improvement...',
        'job-titles': '💼 Matching you to job titles...',
    };

    showLoader(loaderMessages[type] || 'Analyzing...');

    try {
        const response = await fetch(urlMap[type], {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken,
            },
        });

        const data = await response.json();
        hideLoader();

        if (!response.ok) {
            showAlert(data.error || 'Something went wrong.', 'error');
            return;
        }

        // Show results
        const resultsDiv = document.getElementById('analysisResults');
        const resultText = document.getElementById('resultText');
        const radarContainer = document.getElementById('radarChartContainer');

        if (resultsDiv) resultsDiv.classList.remove('hidden');

        // Render markdown
        if (resultText && data.result) {
            resultText.innerHTML = marked.parse(data.result);
        }

        // Render radar chart if available (summary tab)
        if (data.radar_chart && radarContainer) {
            radarContainer.classList.remove('hidden');
            Plotly.newPlot('radarChart', data.radar_chart.data, data.radar_chart.layout, {
                responsive: true,
                displayModeBar: false,
            });
        } else if (radarContainer) {
            radarContainer.classList.add('hidden');
        }

        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
        hideLoader();
        showAlert('Network error. Please try again.', 'error');
        console.error(err);
    }
}

// ─── Submit Gap Analysis ───
async function submitGapAnalysis(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    showLoader('📊 Comparing resume against job description...');

    try {
        const response = await fetch('/analyze/gap/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken,
            },
        });

        const data = await response.json();
        hideLoader();

        if (!response.ok) {
            showAlert(data.error || 'Something went wrong.', 'error');
            return;
        }

        const gapResults = document.getElementById('gapResults');
        if (gapResults) gapResults.classList.remove('hidden');

        // Render Gauge Chart
        if (data.gauge_chart) {
            Plotly.newPlot('gaugeChart', data.gauge_chart.data, data.gauge_chart.layout, {
                responsive: true,
                displayModeBar: false,
            });
        }

        // Render Matching Skills
        const matchingEl = document.getElementById('matchingSkills');
        if (matchingEl && data.result.matching_skills) {
            matchingEl.innerHTML = data.result.matching_skills
                .map(s => `<span class="tag tag-success">✅ ${s}</span>`)
                .join('');
        }

        // Render Missing Skills
        const missingEl = document.getElementById('missingSkills');
        if (missingEl && data.result.missing_skills) {
            missingEl.innerHTML = data.result.missing_skills
                .map(s => `<span class="tag tag-danger">❌ ${s}</span>`)
                .join('');
        }

        // Render Assessment
        const assessmentEl = document.getElementById('assessmentText');
        if (assessmentEl && data.result.overall_assessment) {
            assessmentEl.innerHTML = marked.parse(data.result.overall_assessment);
        }

        // Render Suggestions
        const suggestionsEl = document.getElementById('suggestionsText');
        if (suggestionsEl && data.result.suggestions) {
            const suggestionsHtml = data.result.suggestions
                .map(s => `<li>${s}</li>`)
                .join('');
            suggestionsEl.innerHTML = `<ul>${suggestionsHtml}</ul>`;
        }

        gapResults.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
        hideLoader();
        showAlert('Network error. Please try again.', 'error');
        console.error(err);
    }
}

// ─── Submit LinkedIn Scraper ───
async function submitLinkedIn(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    showLoader('🔍 Scraping LinkedIn job listings...');

    try {
        const response = await fetch('/scraper/linkedin/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken,
            },
        });

        const data = await response.json();
        hideLoader();

        if (!response.ok) {
            showAlert(data.error || 'Scraping failed.', 'error');
            return;
        }

        const resultsDiv = document.getElementById('linkedinResults');
        const cardsDiv = document.getElementById('jobCards');

        if (resultsDiv) resultsDiv.classList.remove('hidden');

        if (data.results && data.results.length > 0) {
            cardsDiv.innerHTML = data.results.map((job, idx) => `
                <div class="job-card animate-fade-up stagger-${Math.min(idx + 1, 6)}" style="margin-bottom: var(--space-md);">
                    <div class="job-card-header">
                        <div class="job-card-logo">${job.company.charAt(0).toUpperCase()}</div>
                        <div>
                            <div class="job-card-title">${escapeHtml(job.title)}</div>
                            <div class="job-card-company">${escapeHtml(job.company)}</div>
                        </div>
                    </div>
                    <div class="job-card-meta">
                        <span>📍 ${escapeHtml(job.location)}</span>
                    </div>
                    <div class="job-card-description" id="jobDesc${idx}">
                        <p>${escapeHtml(job.description)}</p>
                    </div>
                    <div class="job-card-actions">
                        <button class="btn btn-ghost btn-sm" onclick="toggleJobDesc('jobDesc${idx}')">
                            📖 Toggle Description
                        </button>
                        <a href="${escapeHtml(job.url)}" target="_blank" class="btn btn-primary btn-sm">
                            🔗 View on LinkedIn
                        </a>
                    </div>
                </div>
            `).join('');
        } else {
            cardsDiv.innerHTML = `
                <div class="alert alert-info">
                    <span>ℹ️</span> No matching jobs found. Try different search terms.
                </div>
            `;
        }

        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
        hideLoader();
        showAlert('Network error. Please try again.', 'error');
        console.error(err);
    }
}

// ─── Toggle Job Description ───
function toggleJobDesc(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.toggle('expanded');
    }
}

// ─── Export PDF ───
async function exportPDF() {
    showLoader('📥 Generating PDF report...');

    try {
        const response = await fetch('/export/pdf/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        hideLoader();

        if (!response.ok) {
            const data = await response.json();
            showAlert(data.error || 'PDF generation failed.', 'error');
            return;
        }

        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume_analysis_report.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        showAlert('PDF report downloaded successfully!', 'success');

    } catch (err) {
        hideLoader();
        showAlert('Failed to generate PDF.', 'error');
        console.error(err);
    }
}

// ─── Alert Helper ───
function showAlert(message, type = 'info') {
    // Remove existing alerts
    document.querySelectorAll('.floating-alert').forEach(a => a.remove());

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} floating-alert`;
    alert.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        animation: fadeInDown 0.3s ease-out;
    `;

    const icons = { error: '❌', success: '✅', info: 'ℹ️' };
    alert.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> ${escapeHtml(message)}`;

    document.body.appendChild(alert);

    setTimeout(() => {
        alert.style.animation = 'fadeInUp 0.3s ease-out reverse forwards';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// ─── HTML Escape ───
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Navbar scroll effect ───
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(5, 10, 20, 0.95)';
        } else {
            navbar.style.background = 'rgba(5, 10, 20, 0.85)';
        }
    }
});
