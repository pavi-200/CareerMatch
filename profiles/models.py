from django.conf import settings
from django.db import models

from jobs.models import Skill


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=160, blank=True)
    degree = models.CharField(max_length=120, blank=True)
    branch = models.CharField(max_length=120, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    certifications = models.TextField(blank=True)
    preferred_role = models.CharField(max_length=120, blank=True)
    preferred_location = models.CharField(max_length=120, blank=True)
    skills = models.ManyToManyField(Skill, through="UserSkill", related_name="profiles", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def skill_names(self):
        return list(self.skills.values_list("name", flat=True))

    @property
    def completion_percentage(self):
        fields = [self.full_name, self.degree, self.branch, self.preferred_role, self.preferred_location]
        completed = sum(bool(value) for value in fields) + bool(self.skill_names)
        return round(completed * 100 / 6)


class UserSkill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="user_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="user_skills")
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices, default=Proficiency.INTERMEDIATE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["profile", "skill"], name="unique_skill_per_profile")]

    def __str__(self):
        return f"{self.profile}: {self.skill}"
