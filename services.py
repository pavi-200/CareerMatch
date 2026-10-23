from django.db.models import Q

from .models import Job


def search_jobs(query="", location="", job_type="", max_experience="", sort="newest"):
    jobs = Job.objects.filter(is_active=True).prefetch_related("skills")
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(company__icontains=query)
            | Q(description__icontains=query)
            | Q(skills__name__icontains=query)
        ).distinct()
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if max_experience.isascii() and max_experience.isdecimal():
        jobs = jobs.filter(experience_required__lte=int(max_experience))
    ordering = {
        "newest": ("-created_at", "title"),
        "oldest": ("created_at", "title"),
        "title": ("title", "company"),
        "experience": ("experience_required", "-created_at"),
    }
    return jobs.order_by(*ordering.get(sort, ordering["newest"]))
