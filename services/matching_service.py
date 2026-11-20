import re

def _normalize(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())

def _extract_tokens(skill_str):
    if not skill_str:
        return set()
    # Split on comma, semicolon, slash, or plus
    parts = re.split(r'[,;/+]+', skill_str)
    return {p.strip().lower() for p in parts if p.strip()}

def calculate_job_match(worker_profile, job):
    """
    Rule-based skill and location matching algorithm.
    Formula:
      - Skill Match (Max 50 points)
      - Location Match (Max 40 points)
      - Wage Compatibility (Max 10 points)
      Total = 100 points
    """
    if not worker_profile or not job:
        return {
            'score': 0,
            'match_level': 'Low',
            'matched_skills': [],
            'location_match': False,
            'wage_fit': False
        }

    worker_skills = _extract_tokens(worker_profile.skills)
    job_skills = _extract_tokens(job.required_skills)
    worker_location = _normalize(worker_profile.user.location if worker_profile.user else "")
    job_location = _normalize(job.location)

    # 1. Skill Matching (50 points maximum)
    matched_skills = []
    skill_score = 0.0
    if job_skills and worker_skills:
        for js in job_skills:
            # Check exact match or substring match
            for ws in worker_skills:
                if js in ws or ws in js:
                    matched_skills.append(js.title())
                    break
        
        overlap_ratio = len(matched_skills) / len(job_skills)
        skill_score = round(overlap_ratio * 50.0, 1)
    elif not job_skills:
        # If no specific skills required (general helper)
        skill_score = 30.0

    # 2. Location Matching (40 points maximum)
    location_score = 0.0
    location_match = False
    if worker_location and job_location:
        if worker_location == job_location:
            location_score = 40.0
            location_match = True
        elif worker_location in job_location or job_location in worker_location:
            location_score = 30.0
            location_match = True
        else:
            # Check for common keywords (e.g. Mangalore, Bantwal, Udupi, Bangalore)
            worker_words = set(worker_location.split())
            job_words = set(job_location.split())
            if worker_words & job_words:
                location_score = 25.0
                location_match = True

    # 3. Wage Fit (10 points maximum)
    wage_fit = False
    wage_score = 0.0
    expected_wage = worker_profile.expected_wage or 0.0
    if job.wage >= expected_wage:
        wage_score = 10.0
        wage_fit = True
    elif job.wage >= (expected_wage * 0.85):
        wage_score = 5.0
        wage_fit = True

    total_score = min(100, int(round(skill_score + location_score + wage_score)))

    if total_score >= 75:
        match_level = "Excellent Match"
        badge_class = "success"
    elif total_score >= 50:
        match_level = "Strong Match"
        badge_class = "primary"
    elif total_score >= 30:
        match_level = "Fair Match"
        badge_class = "info"
    else:
        match_level = "Low Match"
        badge_class = "secondary"

    return {
        'score': total_score,
        'skill_score': skill_score,
        'location_score': location_score,
        'wage_score': wage_score,
        'match_level': match_level,
        'badge_class': badge_class,
        'matched_skills': sorted(list(set(matched_skills))),
        'location_match': location_match,
        'wage_fit': wage_fit
    }

def get_recommended_jobs(worker_profile, all_jobs=None, limit=12):
    """
    Ranks active jobs based on matching algorithm for a given worker profile.
    """
    from models.job import Job
    if all_jobs is None:
        all_jobs = Job.query.filter_by(status='active').all()

    scored_jobs = []
    for job in all_jobs:
        match_info = calculate_job_match(worker_profile, job)
        scored_jobs.append({
            'job': job,
            'match': match_info
        })

    # Sort descending by match score, then by job created_at
    scored_jobs.sort(
        key=lambda x: (x['match']['score'], x['job'].created_at or 0),
        reverse=True
    )

    if limit:
        return scored_jobs[:limit]
    return scored_jobs
