from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Job, Skill


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "job_type", "is_active", "created_at")
    list_filter = ("job_type", "is_active", "location")
    search_fields = ("title", "company", "description", "location")
    filter_horizontal = ("skills",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)
