from django import forms

from jobs.models import Skill
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        help_text="Separate skills with commas, for example: Python, SQL, Django",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Python, SQL, Django"}),
    )

    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "degree",
            "branch",
            "experience_years",
            "certifications",
            "preferred_role",
            "preferred_location",
        ]
        widgets = {
            "certifications": forms.Textarea(attrs={"rows": 3}),
            "experience_years": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skills"].initial = ", ".join(self.instance.skill_names) if self.instance.pk else ""
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            names = {name.strip() for name in self.cleaned_data["skills"].split(",") if name.strip()}
            skills = []
            for name in sorted(names, key=str.casefold):
                skill, _ = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name})
                skills.append(skill)
            profile.skills.set(skills)
        return profile
