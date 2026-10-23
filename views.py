from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import JobApplication, SavedJob
from .models import Job
from .services import search_jobs


def home(request):
    featured_jobs = Job.objects.filter(is_active=True).prefetch_related("skills")[:6]
    return render(request, "home.html", {"featured_jobs": featured_jobs, "total_jobs": Job.objects.filter(is_active=True).count()})


def job_list(request):
    filters = {
        "query": request.GET.get("q", "").strip(),
        "location": request.GET.get("location", "").strip(),
        "job_type": request.GET.get("job_type", "").strip(),
        "max_experience": request.GET.get("experience", "").strip(),
        "sort": request.GET.get("sort", "newest").strip(),
    }
    jobs = search_jobs(**filters)
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(SavedJob.objects.filter(user=request.user).values_list("job_id", flat=True))
    return render(
        request,
        "jobs/list.html",
        {
            "jobs": jobs,
            "filters": filters,
            "job_types": Job.JobType.choices,
            "sort_options": [("newest", "Newest first"), ("oldest", "Oldest first"), ("title", "Title A–Z"), ("experience", "Least experience")],
            "saved_ids": saved_ids,
        },
    )


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.prefetch_related("skills"), pk=pk, is_active=True)
    saved = request.user.is_authenticated and SavedJob.objects.filter(user=request.user, job=job).exists()
    applied = request.user.is_authenticated and JobApplication.objects.filter(user=request.user, job=job).exists()
    return render(request, "jobs/detail.html", {"job": job, "saved": saved, "applied": applied})


@login_required
def toggle_saved_job(request, pk):
    if request.method != "POST":
        return redirect("job_detail", pk=pk)
    job = get_object_or_404(Job, pk=pk, is_active=True)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
    messages.success(request, "Job saved." if created else "Job removed from saved jobs.")
    if request.POST.get("next") == "saved_jobs":
        return redirect("saved_jobs")
    return redirect("job_detail", pk=pk)
