from django.db import models
import json
import uuid


class Team(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective = models.CharField(null=False, blank=False, max_length=511)
    description = models.TextField(null=True, blank=True)
    generation_progress_percent = models.PositiveSmallIntegerField(default=0)

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
                "questions": role.questions_text,
                "guide": role.guide_text,
                "tasks_string":  role.tasks_list_text or "",
                "image_url": role.image_url
            }
            try:
                retval["team"]["roles"][role.name]["tasks"] = json.loads(role.tasks_list_js_array)
            except:
                print(f"Couldn't parse {role.tasks_list_js_array} on {role.guid}")


        return retval

class Role(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=False, blank=False)
    questions_text = models.TextField(null=True, blank=True)
    guide_text = models.TextField(null=True, blank=True)
    tasks_list_js_array = models.TextField(null=True, blank=True)
    tasks_list_text = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=1023, null=True, blank=True)


    team = models.ForeignKey(Team, on_delete=models.CASCADE)



