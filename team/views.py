from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf import settings
from django.urls import reverse

from team.models import Team, Chat
import requests
import uuid
import random
import os
import time
import openai
from dotenv import load_dotenv
import json
import threading

import re

def approximate_word_count(text):
    '''
    Function that takes a string of text and returns an approximate word count
    '''
    # Remove all non-word characters
    text = re.sub(r'\W', ' ', text)
    # Split the string into a list of words
    words = text.split()
    # Count the words
    count = len(words)
    return count
#test_string = "This is a test string with 12 words"
#print(approximate_word_count(test_string)) # Output: 12 lol
"""
Concepts

- "slow" ai
- building human processes and finding places for ai to assist
  = human teams, optional assistants
- a curious team producing its own FAQ
- remember this team is locked in a box with only its knowledge.
- AIs built to replicate patterns of human communication will necessarily
  function best when they interact like a highly-functional human team:
  keeping morale high, kind words, affirmation... seemingly unproductive
  conversation among computers, but aligned with the human language
  training data
"""

"""
MAYBE TODO
- Gather facts & tasks after every round of chat and present it to the user
  as well as to each agent when prompting for that agent's response.
"""

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
      role: str = "system",
      previous_messages: list = None
):
        max_retries = 5
        for retries in range(0, max_retries):
            try:
                # Use chat completion API
                if not previous_messages:
                    messages = [{"role": role, "content": prompt}]
                else:
                    messages = previous_messages + [{"role": role, "content": prompt}]
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                )
                return (response.choices[0].message.content.strip(), response.usage.total_tokens)
            except openai.error.RateLimitError:
                print(
                    "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.Timeout:
                print(
                    "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.APIError:
                print(
                    "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.APIConnectionError:
                print(
                    "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.InvalidRequestError as e:
                print(
                        f"   *** OpenAI API invalid request. {e} Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and bailing. "
                )
                time.sleep(10)  # Wait 10 seconds and try again
                retries=max_retries
            except openai.error.ServiceUnavailableError:
                print(
                    "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            else:
                break
            
            print(
                "   *** OpenAI API max retries or weird error hit, so bailing on request & returning false."
            )
            return False, 0

def create_and_generate_team(OBJECTIVE):
    print(f'shall I reject {OBJECTIVE} team?')

    prompt = f'Yes or no: is the following objective offensive or inappropriate: "{OBJECTIVE}"? Answer with only yes or no.'
    result, tokens_used = openai_call(prompt, max_tokens=100)
    print("Offensive? "+ result)
    if not result or 'yes' in result.lower():
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
    result, tokens_used = openai_call(prompt, max_tokens=3000)
    print(result)
    print(f"TOKENS USED: {tokens_used}")
    if not result:
        print("something went wrong 2.")
        return


    team.description=result
    team.tokens_used += tokens_used
    team.generation_progress_percent = 10
    team.save()

    context = prompt + result

    role_tasks = {}
    try:
        role_tasks = json.loads(f"{result}")
        print(f"parsed {result} into json {role_tasks}")
    except:
        print("Couldn't parse {result}.")

    valid_json = False
    while not valid_json:
        prompt = f"{context} List the roles on this team as a JavaScript array of strings. RESULT:["
        result, tokens_used = openai_call(prompt)
        print("["+ result)
        print(f"TOKENS USED: {tokens_used}")
        if not result:
            print("something went wrong 3.")
            return
        team.tokens_used += tokens_used
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
        effectively collaborate toward the real-world objective: {OBJECTIVE}."""
        result, tokens_used = openai_call(prompt, max_tokens=3000)
        print(result)
        print(f"TOKENS USED: {tokens_used}")
        if not result:
            print("something went wrong 4.")
            return
        progress_points = progress_points + 1
        team.tokens_used += tokens_used
        team.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
        team.save()

        new_role = team.role_set.create(
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
            print("something went wrong 5.")
            return


        new_role.guide_text =result
        if role in role_tasks:
            if isinstance(role_tasks[role], list):
                print("saving tasks a list")
                new_role.tasks_list_js_array=json.dumps(role_tasks[role])
            elif isinstance(role_tasks[role], dict):
                print("saving tasks as a different list")
                new_role.tasks_list_js_array=json.dumps([role_tasks[role][key] for key in role_tasks[role]])
            else:
                print("saving tasks a string")
                new_role.tasks_list_text=json.dumps(role_tasks[role])
        else:
            print(f"no, {role} not in {role_tasks}")

        new_role.save()

        progress_points = progress_points + 1
        team.tokens_used += tokens_used
        team.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
        team.save()

        if render_images:
            generate_stranger = False
            mascfem = random.choice(["masculine ", "feminine ", ""])
            #city = "New York City"
            city = "Atlanta"
            #city = random.choice(["New York City", "Atlanta"])
            prompt = f"3D rendered cartoon avatar of {mascfem}{role} from {city}, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, NOT ugly, NOT disfigured, NOT bad"

            max_retries = 5

            for retries in range(0, max_retries):
                try:
                    if generate_stranger:
                        prompt = f"3D rendered cartoon avatar of {mascfem}human from New York City, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"
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
                    continue
                except openai.error.Timeout:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                    continue
                except openai.error.APIError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                    continue
                except openai.error.APIConnectionError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                    continue
                except openai.error.InvalidRequestError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Generating stranger image instead. ***"
                    )
                    generate_stranger = True
                    continue
                except openai.error.ServiceUnavailableError:
                    print(f"***Error generating image for {role}.")
                    print(
                        "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
                    )
                    time.sleep(10)  # Wait 10 seconds and try again
                    continue
                else:
                    print(f"***Error generating image for {role}.")
                    break
            print("done with image")
            progress_points = progress_points + 1
            team.generation_progress_percent = round(base_progress_percent + ((100-base_progress_percent)*(progress_points/total_progress_points)))
            team.save()

    end_time = time.time()
    print(end_time)
    total_time_mins = (end_time - start_time)/60
    print(f"That took {total_time_mins} minutes. Serving page, then saving images.")

    for idx, role in enumerate(team.role_set.all()):
        file_name = str(uuid.uuid4()) + ".png"
        file_path = os.path.join(settings.DOWNLOAD_IMAGES_ROOT, file_name)
        img_data = requests.get(role.image_url).content
        with open(file_path, 'wb') as handler:
            handler.write(img_data)
            print(f"Downloaded and wrote to {file_path}")
            role.image_url = f'{settings.DOWNLOAD_IMAGES_URL}/{file_name}'
            role.save()
            print(f"Saved image url to our image. {role.image_url} now")
    
    end_time = time.time()
    total_time_mins = (end_time - start_time)/60

    cost_per_token = (0.002/1000)
    cost_per_image = (0.018)
    cost = (team.tokens_used * cost_per_token) + (cost_per_image * team.role_set.count())
    print(f"After downloading {team.role_set.count()} images, that took {total_time_mins} minutes and {team.tokens_used} tokens (${cost}).")



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
    if len(objective) > 511:
        objective = None
        guide = "denied"
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
            template_context["progress_message"] = f"{team.objective} team is in the queue."
        elif team.generation_progress_percent == 10:
            template_context["progress_message"] = f"Team {team.objective} is generating..."
        elif team.generation_progress_percent == 20:
            template_context["progress_message"] = f"{team.objective} team defined. Working on specifics."
        else:
            number_roles_created = len(team.role_set.all())
            number_roles_with_guide = len(team.role_set.filter(guide_text__isnull=False))
            number_roles_completed = len(team.role_set.filter(image_url__isnull=False))
            if number_roles_completed == number_roles_created:
                template_context["progress_message"] = f"Generating role #{number_roles_created+1} for {team.objective} team."
            elif number_roles_with_guide == number_roles_created:
                template_context["progress_message"] = f"Generating image for role #{number_roles_created} on team {team.objective}."
            else:
                template_context["progress_message"] = f"Generating handbook for role #{number_roles_created} on the {team.objective} team."

        return TemplateResponse(request, "progress.html", template_context)

    return TemplateResponse(request, "team.html", template_context)


def test_generate_profile_image(request):
    role = request.GET["role"]
    mascfem = request.GET.get('mascfem', random.choice(["masculine", "feminine"]))
    add = request.GET.get('add','')
    city = request.GET.get('city', 'New York City')
    prompt = f"3D rendered cartoon avatar of {mascfem} {add} {role} from {city}, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"

    print(f"trying {prompt}")
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    return HttpResponse(f'<img src="{image_url}">')

@require_GET
def home(request):
    template_context = {}
    sample_size = 100

    template_context["recent"] = Team.objects.filter(private=False).order_by('-created')[:sample_size]
    try:
        pks = random.sample([val for val in Team.objects.filter(private=False).values_list('pk', flat=True)], sample_size)
    except ValueError:
        pks = [val for val in Team.objects.filter(private=False).values_list('pk', flat=True)]

    template_context["random"] = Team.objects.filter(pk__in=pks)
    return TemplateResponse(request, "home.html", template_context)

@require_GET
def create_team_chat_by_guid(request, team_guid):
    """
    create a new chat
    return redirect to the new chat
    """
    team = Team.objects.get(guid=team_guid)
    new_chat = Chat.objects.create(team_id=team_guid)
    new_chat.save()
    guid = new_chat.guid
    human_role_guids = request.GET.get('me', '').split(' ')

    for role in new_chat.team.role_set.all():
        if str(role.guid) in human_role_guids:
            print(f"Not summarizing for human role {role.name}")
            new_chat.human_roles.add(role)
            continue
        else:
            print(f"{role.guid} not in human guids {human_role_guids}")

        print(f"Making AI system prompt for role {role.name}")
        #prompt = f'Summarize the following handbook into a directive to give to an AI agent assuming the role of {role.name}: {role.guide_text}'
        #result, tokens_used = openai_call(prompt, max_tokens=3000)
        #print(f"TOKEN USED {tokens_used}")
        result = f"""You are an expert in the role of {role.name} on this team. Team objective: '{team.objective}'.
                You read the latest chat messages and summary and respond with a question, a task, a factual
                response to a question, or silence. You always begin responses with '{role.name}:'.
                Your responsibilities are:{role.tasks_list_js_array}{role.tasks_list_text}"""
        role.ai_prompt = result
        role.save()

    print(f"Made AI agents for {new_chat.team}.")
    return HttpResponseRedirect(reverse('chat-by-guid', args=(guid,)))

def chat_by_guid(request, guid=None):
    human_input = request.POST.get('human_input', None)
    human_role_name = request.POST.get('human_role_name', None)
    full_meeting = request.GET.get('full_meeting', None)

    template_context = {}
    try:
        chat = Chat.objects.get(guid=guid)
    except:
        chat = None

    if not chat:
        return TemplateResponse(request, "chat.html", {})

    brand_new_chat=False
    if not chat.log and not chat.log_historical:
        initial_chat_log = f"""
        # CHAT LOG - TEAM OBJECTIVE = {chat.team.objective}
        
        Moderator: Team, begin work on your objective. Good luck.

        """
        chat.log = initial_chat_log
        chat.save()
        brand_new_chat=True
    
    last_human_role_name = human_role_name
    possible_human_role_names = [role.name for role in chat.human_roles.all()]
    
    waiting_for_human_input = False
    if not full_meeting and not brand_new_chat and not last_human_role_name:
        waiting_for_human_input = True
        template_context["human_role_name"] = "Moderator"
    if human_input and human_role_name:
        chat.log += f"\n\n{human_role_name}: {human_input}\n\n"
        chat.save()
    

    summary = None
    restart_role_ring_now = False
    print(f"{ waiting_for_human_input } - human turn?")
    while not waiting_for_human_input:
        print(f"Rotating through all roles in team {chat.team}")
        for role in chat.team.role_set.all():
            if restart_role_ring_now:
                # Things got summarized so we have to start the chat over.
                restart_role_ring_now = False
                break
        
            # move through the order until passing the last speaking human, as long as that human was in the list
            if last_human_role_name in possible_human_role_names:
                if role.name == last_human_role_name:
                    last_human_role_name = None
                continue
            
            print(f"Chatting with role: {role}")
            if role.name in possible_human_role_names:
                print(f"Found a human: {role}")
                waiting_for_human_input=True
                template_context["human_role_name"] = role.name
                break

            system_chat_instructions = f"""{role.ai_prompt}"""
            #Respond with a question, a command, or provide a factual response to a previous question addressed to {role.name}. Or be silent.
            #Begin responses with your role name.
            #Stop responding after you ask a question or give a command.
            #Whenever it is time for another person to respond stop responding and remain silent.
            
            # Summarize chat so far.
            system_prompt = f"""{system_chat_instructions}"""
            user_prompt = f"""{chat.log or ""}\n\n"""
            previous_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt }
                    ]
            role = "assistant"
            prompt = ""

            result, tokens_used = openai_call(prompt, max_tokens=500, previous_messages=previous_messages)
            print(result)
            print(f"TOKEN USED {tokens_used}")
            if result is False:
                # Chat's too long... 
                # summarize it.
                chatlog = chat.log
                print(f"Summarizing Chat {chat.guid} so far")
                #summary_system_prompt = """You summarize a chat log into a project status recap. The recap always lists the top 5 tasks the team is working on as a todo list with assignees and the most important data points per task."""
                #summary_system_prompt = f"""You summarize a chat log into a brief project status recap. The recap includes two short sections: * Answers to the important questions so far * the top 5 currently incomplete tasks the team is working on as a todo list with assignees """
                #summary_system_prompt = """You summarize a meeting log into a list of precisely what actions each team member will take before the next meeting and factoids discovered by the team."""

                summary_system_prompt = """Produce a list of items stated as a fact."""
                summary_messages = [{"role": "system", "content": summary_system_prompt }]
                # summary must not fail. a token is about 3/4 of a word.
                token_count = approximate_word_count(f"{summary_system_prompt}{chatlog}") * (4/3)
                max_token_count = 1000

                if token_count > max_token_count:
                    scale_factor = max_token_count/token_count
                    substrlen = int(len(chatlog)*scale_factor)
                    chatlog = chatlog[-substrlen:]

                result, tokens_used = openai_call(chatlog,role="user", max_tokens=max_token_count, previous_messages=summary_messages)
                print(result)
                print(f"TOKENS USED {tokens_used}")
                summary = result
                end_of_session_message = "## END OF MEETING"
                # save the log so the chat can be rendered as old log + summary + current log
                chat.log_historical = f"{chat.log_historical}\n{chat.log}\n"
                # but start over with chat.log = just the summary as chat.log
                chat.log = f"""{end_of_session_message}
                {summary}

                # CHAT LOG - TEAM OBJECTIVE = {chat.team.objective}
    
                Moderator: Welcome back, team. Continue work on your objective. Good luck.
                """
                chat.save()

                # and then, oddly, restart the role ring. this is so shameful.
                restart_role_ring_now = True
            else:
                chat.log += result + "\n\n"
                chat.save()
       
        # Done with the role ring 
        if len(possible_human_role_names) == 0:
            print(f"no human role names possible")
            if summary or not full_meeting:
                waiting_for_human_input=True
                print(f"waiting for human input")
                template_context["human_role_name"] = "Moderator"
            else:
                print(f"Full meeting - Not waiting for human input after role ring for {chat.team}.")

    template_context["chat"] = chat
    return TemplateResponse(request, "chat.html", template_context)

