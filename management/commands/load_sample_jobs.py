import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from jobs.models import Job, Skill


class Command(BaseCommand):
    help = "Import or update job listings from dataset/jobs.csv."

    def handle(self, *args, **options):
        csv_path = Path(__file__).resolve().parents[3] / "dataset" / "jobs.csv"
        if not csv_path.is_file():
            raise CommandError(f"Sample jobs file was not found: {csv_path}")
        created_count = 0
        updated_count = 0
        with csv_path.open(encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            required = {"title", "company", "description", "location", "experience_required", "job_type", "skills"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise CommandError(f"CSV must include these columns: {', '.join(sorted(required))}")
            for row in reader:
                job, created = Job.objects.update_or_create(
                    title=row["title"].strip(),
                    company=row["company"].strip(),
                    defaults={
                        "description": row["description"].strip(),
                        "location": row["location"].strip(),
                        "experience_required": int(row["experience_required"]),
                        "job_type": row["job_type"].strip(),
                        "is_active": True,
                    },
                )
                job.skills.set(
                    [
                        Skill.objects.get_or_create(name=name.strip())[0]
                        for name in row["skills"].split("|")
                        if name.strip()
                    ]
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        self.stdout.write(self.style.SUCCESS(f"Loaded {created_count} new and updated {updated_count} existing jobs."))
