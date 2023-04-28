from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf import settings
from django.urls import reverse

from team.models import Team

import os
import time
import openai
from dotenv import load_dotenv
import json
import threading



OPENAI_API_KEY=settings.OPENAI_API_KEY

# Model: GPT, LLAMA, HUMAN, etc.
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")).lower()

# Model configuration
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.5))

# Configure OpenAI
openai.api_key = OPENAI_API_KEY
render_images = True


def openai_call(
      prompt: str,
      model: str = LLM_MODEL,
      temperature: float = OPENAI_TEMPERATURE,
      max_tokens: int = 100,
):
    while True:
        try:
            # Use chat completion API
            messages = [{"role": "system", "content": prompt}]
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
            )
            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            print(
                "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.Timeout:
            print(
                "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.APIError:
            print(
                "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.APIConnectionError:
            print(
                "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.InvalidRequestError:
            print(
                "   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.ServiceUnavailableError:
            print(
                "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        else:
            break

def create_and_generate_team(OBJECTIVE):
    print(f'shall I reject {OBJECTIVE} team?')

    prompt = f'Yes or no: is the following objective offensive or inappropriate: "{OBJECTIVE}"? Answer with only yes or no.'
    result = openai_call(prompt, max_tokens=100)
    print("Offensive? "+ result)
    if 'yes' in result.lower():
        return None

    # make new team, get guid
    new_team = Team(objective=OBJECTIVE)
    new_team.save()
    guid = new_team.guid
    print("launching thread for generate_team")

    t = threading.Thread(target=generate_team,args=[OBJECTIVE, guid], daemon=True)
    t.start()

    print("thread for generate_team launched")
    return guid

def generate_team(OBJECTIVE, guid):
    print(f"generating team for {OBJECTIVE} guid {guid}")
    start_time = time.time()

    progress_points_total = 0

    # fetch Team instance
    print(f"fetching team objects for {OBJECTIVE} guid {guid}")
    team = Team.objects.get(guid=guid)
    print(f"got team objects for {OBJECTIVE} guid {guid}")
    if not team:
        print("something went wrong.")
        return

    context = ""
    print(f"prompt building for {OBJECTIVE} guid {guid}")
    prompt = f"""
        OBJECTIVE: {OBJECTIVE}
        TASK: Write instructions for a team of humans to execute. Respond with a JSON object whose keys are
        unique role names on the team and each key contains a task list for that unique role.
        RESPONSE (JSON format only):"""
    print(f"calling openai for team for {OBJECTIVE} guid {guid}")
    result = openai_call(prompt, max_tokens=3000)
    print(result)

    team.description=result
    team.generation_progress_percent = 10
    team.save()

    context = prompt + result

    role_tasks = {}
    try:
        role_tasks = json.loads(f"{result}")
        # used later
    except:
        print("Couldn't parse the team description this time.")

    valid_json = False
    while not valid_json:
        prompt = f"{context} List the roles on this team as a JavaScript array of strings. RESULT:["
        result = openai_call(prompt)
        print("["+ result)
        team.generation_progress_percent = 20 
        team.save()


        context = prompt + result

        try:
            roles = json.loads(f"[{result}")
            valid_json = True
        except:
            prompt = f"{context} That was not valid JavaScript array syntax. Try again:\n"

    progress_points = 0
    steps_per_role = 3
    total_progress_points = len(roles)*steps_per_role
    base_progress_percent = 20
    for idx, role in enumerate(roles):
        loop_context = context
        prompt = f"""{loop_context}
        You are a new member on this team, assuming the role of {role}. List the questions you want to ask an
        expert in this role so they can give you the answers that will make you successful at your tasks and able to
        effectively collaborate toward the objective: {OBJECTIVE}."""
        result = openai_call(prompt, max_tokens=3000)
        print(result)
        progress_points = progress_points + 1
        team.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
        team.save()

        new_role = team.role_set.create(
                name=role,
                questions_text=result,
        )

        loop_context = prompt + result

        prompt = f"""{loop_context}
                You are an expert in the role of {role} on this team. Generate a handbook for the new member in this
                role using Markdown format. In it, answer each of the new member's specific questions.
                Also include a guide which describes step-by-step a typical workday that the person in this role
                should expect to do."""
        result = openai_call(prompt, max_tokens=3000)
        print(result)


        new_role.guide_text =result
        if role in role_tasks:
            if isinstance(role_tasks[role], list):
                print("saving tasks a list")
                new_role.tasks_list_js_array=json.dumps(role_tasks[role])
            elif isinstance(role_tasks[role], dict):
                print("saving tasks as a different list")
                new_role.tasks_list_string=json.dumps([role_tasks[role][key] for key in role_tasks[role]])
            else:
                print("saving tasks a string")
                new_role.tasks_list_string=json.dumps(role_tasks[role])
        else:
            print(f"no, {role} not in {role_tasks}")

        new_role.save()

        progress_points = progress_points + 1
        team.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
        team.save()

        if render_images:
            prompt = f"3D rendered cartoon avatar of {role} from New York City, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"

            max_retries = 5
            for retries in range(0, max_retries):
                try:
                    response = openai.Image.create(
                        prompt=prompt,
                        n=1,
                        size="512x512"
                    )
                    image_url = response['data'][0]['url']
                    print(image_url)
                    new_role.image_url=image_url
                    new_role.save()
                    break
                except openai.error.RateLimitError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                except openai.error.Timeout:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                except openai.error.APIError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                except openai.error.APIConnectionError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                except openai.error.InvalidRequestError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                except openai.error.ServiceUnavailableError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                else:
                    print(f"***Error generating image for {role}.")
                    break
            progress_points = progress_points + 1
            team.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
            team.save()

        

    end_time = time.time()
    print(end_time)
    total_time_mins = (end_time - start_time)/60
    print(f"That took {total_time_mins} minutes.")
    return



@require_POST
def team(request):
    """
    POST with objective
     launch thread: generate_job(), which updates Team after each response from openai
     respond with redir to GET /team/GUID
    """

    objective = request.POST.get('objective', "")
    context = {}
    guid = "no-objective"
    if objective:
        # if this fails, guid is None, team-by-guid's guid is None
        guid = create_and_generate_team(objective) or "denied"
    return HttpResponseRedirect(reverse('team-by-guid', args=(guid,)))

def team_by_guid(request, guid=None, format=None):
    """
    look up team info from db
    if format=='json', render json page, end

    if team is complete, render team page
    else render progress page, which will request JSON 
    """

    if not guid:
        # let the template handle a missing team i guess
        print("no guid. rejected.")
        return TemplateResponse(request, "team.html", {})

    print(f"look up team by guid {guid}.")
    try:
        team = Team.objects.get(guid=guid)
    except:
        team = None

    if not team:
        # let the template handle a missing team i guess
        print("no team by that guid")
        return TemplateResponse(request, "team.html", {})

    template_context = team.get_template_context()
    if format and format.lower()=='json':
        print("serving up json")
        return HttpResponse(json.dumps(template_context))

    if team.generation_progress_percent < 100:
        print(f"generation progress is {team.generation_progress_percent}")

        if team.generation_progress_percent == 0:
            template_context["progress_message"] = "Queued."
        elif team.generation_progress_percent == 10:
            template_context["progress_message"] = "Now generating your team."
        elif team.generation_progress_percent == 20:
            template_context["progress_message"] = "Got your team defined. Working on specifics."
        else:
            number_roles_created = len(team.role_set.all())
            number_roles_with_guide = len(team.role_set.filter(guide_text__isnull=False))
            number_roles_completed = len(team.role_set.filter(image_url__isnull=False))
            if number_roles_completed == number_roles_created:
                template_context["progress_message"] = f"Generating role #{number_roles_created+1} for your team."
            elif number_roles_with_guide == number_roles_created:
                template_context["progress_message"] = f"Generating image for role #{number_roles_created}."
            else:
                template_context["progress_message"] = f"Generating handbook for role #{number_roles_created}."

        return TemplateResponse(request, "progress.html", template_context)

    return TemplateResponse(request, "team.html", template_context)


def test_generate_profile_image(request):
    role = request.GET["role"]
    add = request.GET.get('add','')
    prompt = f"3D rendered cartoon avatar of {add} {role} from New York City, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"

    print(f"trying {prompt}")
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    return HttpResponse(f'<img src="{image_url}">')
