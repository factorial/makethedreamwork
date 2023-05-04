from django.conf import settings
from django.db import models
from django.utils import timezone

from team.openai import openai_call, openai_image
import requests
import os
import openai
import json
import time
import uuid
import threading
import random


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

    @classmethod
    def create_and_generate_team(cls, OBJECTIVE):
        print(f'Creating & generating team. First, shall I reject {OBJECTIVE} team?')

        prompt = f'Yes or no: is the following objective offensive or inappropriate: "{OBJECTIVE}"? Answer with only yes or no.'
        result, tokens_used = openai_call(prompt, max_tokens=100)
        print("Offensive? "+ result)
        if not result or 'yes' in result.lower():
            return None

        # make new team, get guid
        new_team = cls(objective=OBJECTIVE)
        new_team.save()
        guid = new_team.guid
        print(f"Launching thread to generate_team {new_team}...")

        t = threading.Thread(target=Team.generate_team,args=[new_team], daemon=True)
        t.start()

        print(f"Thread for generate_team {new_team} launched.")
        return guid

    def generate_team(self):
        print(f"Generating team for {self.objective} guid {self.guid}")
        start_time = time.time()

        progress_points_total = 0

        context = ""
        print(f"Prompt building for team {self}")
        prompt = f"""
            OBJECTIVE: {self.objective}
            TASK: Write instructions for a team of humans to execute. Respond with a JSON object whose keys are
            unique role names on the team and each key contains a task list for that unique role.
            RESPONSE (JSON format only):"""
        print(f"Calling openai for team {self}")
        result, tokens_used = openai_call(prompt, max_tokens=3000)
        print(result)
        print(f"TOKENS USED: {tokens_used}")
        if not result:
            print(f"Something went wrong getting team roles for {self}.")
            return

        self.description=result
        self.tokens_used += tokens_used
        self.generation_progress_percent = 10
        self.save()

        context = prompt + result

        role_tasks = {}
        try:
            role_tasks = json.loads(f"{result}")
            print(f"Parsed {self} into json {role_tasks}")
        except:
            print("Couldn't parse {result}. No role_tasks for {self}")

        valid_json = False
        while not valid_json:
            prompt = f"{context} List the roles on this team as a JavaScript array of strings. RESULT:["
            result, tokens_used = openai_call(prompt)
            result = "["+result
            print(result)
            print(f"TOKENS USED: {tokens_used}")
            if not result:
                print(f"Something went wrong getting openai JS array roles out of team description for {self}.")
                return
            self.tokens_used += tokens_used
            self.generation_progress_percent = 20 
            self.save()

            context = prompt + result

            try:
                roles = json.loads(f"{result}")
                valid_json = True
            except:
                print(f"Something went wrong PARSING openai's JS array roles out of team description for {self} Asking again forever.")
                prompt = f"{context} That was not valid JavaScript array syntax. Try again:\n"

        progress_points = 0
        steps_per_role = 3
        total_progress_points = len(roles)*steps_per_role
        base_progress_percent = 20
        for role in roles:
            print(f"Generating role {role} for {self}...")
            loop_context = context
            prompt = f"""{loop_context}
            You are a new member on this team, assuming the role of {role}. List the questions you want to ask an
            expert in this role so they can give you the answers that will make you successful at your tasks and able to
            effectively collaborate toward the real-world objective: {self.objective}."""
            result, tokens_used = openai_call(prompt, max_tokens=3000)
            print(result)
            print(f"TOKENS USED: {tokens_used}")
            if not result:
                print("Something went wrong getting new member questions for {role}.")
                return
            progress_points = progress_points + 1
            self.tokens_used += tokens_used
            self.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
            self.save()

            new_role = self.role_set.create(
                    name=role,
                    questions_text=result,
            )

            loop_context = prompt + result

            prompt = f"""{loop_context}
                    You are an expert in the role of {role} on this team. Generate a handbook for the new member in this
                    role using Markdown format. In it, answer the new member's specific questions in depth.
                    Also include in the handbook a guide which describes step-by-step a typical day in the life of a person in this role
                    on this team."""
            result, tokens_used = openai_call(prompt, max_tokens=3000)
            print(result)
            print(f"TOKENS USED: {tokens_used}")
            if not result:
                print("Something went wrong getting expert answers for {role}.")
                return

            new_role.guide_text =result
            if role in role_tasks:
                print(f"Yes, {role} is in {role_tasks}")
                if isinstance(role_tasks[role], list):
                    print("Saving tasks as a list from list")
                    new_role.tasks_list_js_array=json.dumps(role_tasks[role])
                elif isinstance(role_tasks[role], dict):
                    print("Saving tasks as a list from dict")
                    new_role.tasks_list_js_array=json.dumps([role_tasks[role][key] for key in role_tasks[role]])
                else:
                    print("Saving tasks as a string")
                    new_role.tasks_list_text=json.dumps(role_tasks[role])
            else:
                print(f"No, {role} is not in {role_tasks}, so this role gets no tasks.")

            new_role.save()

            progress_points = progress_points + 1
            self.tokens_used += tokens_used
            self.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
            self.save()

            new_role.generate_image()

            progress_points = progress_points + 1
            self.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
            self.save()

        end_time = time.time()
        print(end_time)
        total_time_mins = (end_time - start_time)/60
        print(f"Generating {self} took {total_time_mins} minutes. Now downloading images from openai...")

        for role in self.role_set.all():
            role.persist_image()
        
        end_time = time.time()
        total_time_mins = (end_time - start_time)/60

        # calculate_cost()
        cost_per_token = (0.002/1000)
        cost_per_image = (0.018)
        cost = (self.tokens_used * cost_per_token) + (cost_per_image * self.role_set.count())
        print(f"After downloading {self.role_set.count()} images, {self} took {total_time_mins} minutes & {self.tokens_used} tokens (${cost}).")



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

    def generate_image(self):
        print(f"Generating image for {self}")
        
        mascfem = random.choice(["masculine ", "feminine ", ""])
        city = "Atlanta"
        prompt = f"3D rendered cartoon avatar of {mascfem}{self.name} from {city}, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, NOT ugly, NOT disfigured, NOT bad"

        new_image_url = openai_image(prompt=prompt)
        if not new_image_url:
            # try generating a stranger instead
            prompt = f"3D rendered cartoon avatar of {mascfem}person, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"
            new_image_url = openai_image(prompt=prompt)

        print(f"Response generating image for {self}: {new_image_url}")
        if new_image_url:
            self.image_url=new_image_url
            self.save()
        else:
            print(f"That's a major error generating image for {self}")

    def persist_image(self):
        file_name = str(uuid.uuid4()) + ".png"
        file_path = os.path.join(settings.DOWNLOAD_IMAGES_ROOT, file_name)
        print(f"Downloading {self.image_url} and writing to {file_path}")
        img_data = requests.get(self.image_url).content
        with open(file_path, 'wb') as handler:
            handler.write(img_data)
            self.image_url = f'{settings.DOWNLOAD_IMAGES_URL}/{file_name}'
            self.save()
            print(f"Saved image. It's at {self.image_url} now")

class Chat(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log = models.TextField(null=True, blank=True)
    log_historical = models.TextField(null=True, blank=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    human_roles =  models.ManyToManyField(Role)

    def __str__(self):
        return f"Chat ({self.guid}) for {self.team.objective} team"


