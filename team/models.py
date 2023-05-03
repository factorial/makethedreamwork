from django.db import models
import json
import uuid
from django.utils import timezone


class Team(models.Model):
    created = models.DateTimeField(default=timezone.now)
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective = models.CharField(null=False, blank=False, max_length=511)
    description = models.TextField(null=True, blank=True)
    generation_progress_percent = models.PositiveSmallIntegerField(default=0)
    private = models.BooleanField(default=False, null=False)
    tokens_used = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.objective} ({self.guid}) private={self.private} tokens_used={self.tokens_used}"

    def get_template_context(self):
        retval = {
                "generation_progress_percent": self.generation_progress_percent,
                "team": {
                    "objective": self.objective,
                    "description": self.description,
                    "roles": {
                    }
                }
        }

        for role in self.role_set.all():
            retval["team"]["roles"][role.name] = {
                "role": role,
                "questions": role.questions_text,
                "guide": role.guide_text,
                "tasks_string":  role.tasks_list_text or "",
                "image_url": role.image_url
            }
            try:
                retval["team"]["roles"][role.name]["tasks"] = json.loads(role.tasks_list_js_array)
            except:
                if role.tasks_list_js_array:
                    print(f"Couldn't parse {role.tasks_list_js_array} on {role.guid} which is a {role.name}")


        return retval

class Role(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=False, blank=False)
    questions_text = models.TextField(null=True, blank=True)
    guide_text = models.TextField(null=True, blank=True)
    tasks_list_js_array = models.TextField(null=True, blank=True)
    tasks_list_text = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=1023, null=True, blank=True)
    ai_prompt = models.TextField(null=True, blank=True)


    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.guid}) on {self.team.objective} team"


class Chat(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log = models.TextField(null=True, blank=True)
    log_historical = models.TextField(null=True, blank=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    human_roles =  models.ManyToManyField(Role)

    def __str__(self):
        return f"Chat ({self.guid}) for {self.team.objective} team"


