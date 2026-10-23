from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from applications.models import JobApplication, SavedJob
from .models import Job, Skill


class JobWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="candidate", password="strong-test-password-123")
        self.job = Job.objects.create(
            title="Python Developer",
            company="Example Co",
            description="Build Python systems and services.",
            location="Bengaluru",
        )
        self.job.skills.add(Skill.objects.create(name="Python"))

    def test_search_finds_job_by_skill_and_location(self):
        response = self.client.get(reverse("job_list"), {"q": "Python", "location": "Bengaluru"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")

    def test_save_job_toggles_and_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("toggle_saved_job", args=[self.job.pk]))
        self.assertRedirects(response, reverse("job_detail", args=[self.job.pk]))
        self.assertTrue(SavedJob.objects.filter(user=self.user, job=self.job).exists())
        self.client.post(reverse("toggle_saved_job", args=[self.job.pk]))
        self.assertFalse(SavedJob.objects.filter(user=self.user, job=self.job).exists())
        response = self.client.get(reverse("toggle_saved_job", args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)

    def test_duplicate_applications_are_prevented(self):
        self.client.force_login(self.user)
        url = reverse("apply_to_job", args=[self.job.pk])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(JobApplication.objects.filter(user=self.user, job=self.job).count(), 1)

    def test_search_results_can_be_sorted_by_title(self):
        other_job = Job.objects.create(
            title="Analyst",
            company="Another Co",
            description="Analyze business data.",
            location="Mumbai",
        )
        response = self.client.get(reverse("job_list"), {"sort": "title"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["jobs"]), [other_job, self.job])
