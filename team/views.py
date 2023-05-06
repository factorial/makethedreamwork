from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf import settings
from django.urls import reverse

from team.models import Team, Chat
from team.openai import openai_call, openai_image
from team.utils import approximate_word_count
from team import prompts

import requests
import uuid
import random
import os
import time
import openai
import json
import threading
import re

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
- AI agent and the context they create lives only as long as the max token length, then another
  generation must pick up where the previous left off, using only a lossy summary
  as its guide. Accuracy in summary is the hard thing in LLMs.

"""

"""
MAYBE TODO
- UI that allows user to reply directly to comments from AI, effectively repeating 
  user input directly before it's the AI target user's turn to speak.
- Let users sign up and volunteer for roles to make human teams with other users,
  maybe drop them in a discord.
- Gather facts & tasks after every round of chat and keep a running list
  present it to the user as well as maybe to each agent when prompting 
  for that agent's response.
- UI that lets user pin comments to be remembered especially in summary
- UI that lets user give one agent focus, letting them request 
  longer completions and prompting differently to get detailed response.
- UI for standard commands like 
  You have all completed your tasks. Please share what you learned.
  Everyone list your next todo item.
"""

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
        guid = Team.create_and_generate_team(objective) or "denied"
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

    template_context["moderator_prompt"] = prompts.TASK_FINDER
    return TemplateResponse(request, "team.html", template_context)


def test_generate_profile_image(request):
    role = request.GET["role"]
    mascfem = request.GET.get('mascfem', random.choice(["masculine", "feminine"]))
    add = request.GET.get('add','')
    city = request.GET.get('city', 'New York City')
    prompt = prompts.AVATAR_FROM_CITY.format(mascfem=mascfem, role=role, city=city, add=add)
    print(f"trying {prompt}")
    image_url = openai_image(prompt)
    print(image_url)
    return HttpResponse(f'<img src="{image_url}">')

def test_generate_any_image(request):
    prompt = request.GET.get("prompt", "")
    print(f"trying {prompt}")
    image_url = openai_image(prompt)
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
    new_chat = team.generate_chat(human_role_guids=request.GET.get('me', '').split(' '))
    mp=request.GET.get('moderator_prompt', None)
    if mp:
        qs = f"?moderator_prompt={mp}"
    else:
        qs = ""
    return HttpResponseRedirect(reverse('chat-by-guid', args=(new_chat.guid,))+qs)

def chat_by_guid(request, guid=None):
    human_input = request.POST.get('human_input', None)
    human_role_name = request.POST.get('human_role_name', None)
    full_meeting = request.GET.get('full_meeting', None)
    moderator_prompt = request.GET.get('moderator_prompt', prompts.TASK_FINDER)

    template_context = {}
    try:
        chat = Chat.objects.get(guid=guid)
    except:
        chat = None

    if not chat:
        return TemplateResponse(request, "chat.html", {})

    brand_new_chat=False
    if not chat.log and not chat.log_historical:
        initial_chat_log = f"""# CHAT LOG - TEAM OBJECTIVE = {chat.team.objective}

Moderator: Team, begin work on your objective. Good luck.
"""
        chat.log = initial_chat_log
        chat.save()
        brand_new_chat=True
    
    last_human_role_name = human_role_name
    possible_human_role_names = [role.name for role in chat.human_roles.all()]

    default_human_role_name = "Moderator"
    if default_human_role_name.lower() in [name.lower() for name in chat.team.role_set.all().values_list('name', flat=True)]:
        default_human_role_name = "M.C."
    
    waiting_for_human_input = False
    if not full_meeting and not brand_new_chat and not last_human_role_name:
        waiting_for_human_input = True
        template_context["human_role_name"] = default_human_role_name
    if human_input and human_role_name:
        chat.log += f"\n\n{human_role_name}: {human_input}\n\n"
        chat.save()
    

    summary = None
    print(f"{ waiting_for_human_input } - human turn?")
    while not waiting_for_human_input:
        print(f"Rotating through all roles in team {chat.team}")
        role_list = []
        for role in chat.team.role_set.all():
            role_list.append(role)
            role_list.append(None)

        for idx, role in enumerate(role_list):
            # if role is None, do the interstitial thing that happens after every role
            # eventually let humans be the interstial from previous requests they made for a specific role
            print(f"Chatting with role: {role}")
            if role is None:
                try:
                    next_role_name = role_list[idx+1].name
                except:
                    next_role_name = role_list[0].name

                system_prompt = moderator_prompt.format(role=next_role_name)
                previous_messages = [ {"role": "system", "content": system_prompt} ]
                openai_role = "user"
                prompt = chat.log
                print(f"Moderating with {system_prompt}")
                result, tokens_used = openai_call(prompt,role=openai_role, max_tokens=500, previous_messages=previous_messages)
                print(result)
                if result:
                    chat.log += f"\n{default_human_role_name}: {result}\n\n"
                    chat.save()
                continue
                    

            # move through the order until passing the last speaking human, as long as that human was in the list
            if last_human_role_name in possible_human_role_names:
                if role.name == last_human_role_name:
                    last_human_role_name = None
                continue
            
            if role.name in possible_human_role_names:
                print(f"Found a human: {role}")
                waiting_for_human_input=True
                template_context["human_role_name"] = role.name
                break

            # TODO HERE: remodel chat as list of messages so we can make previous_messages mark "assistant"
            # all the previous messages from this role.
            # Then, refactor each role into two system prompts: info sharing, then task suggestion. each task is
            # either info gathering or other (thus, necessary for a person to do and eternally undone unless human says so)
            # then maybe make moderator a permanent fixture of this structure who summarizes each group of messages into tasks & facts?
            system_prompt = f"""{role.ai_prompt}"""
            user_prompt = f"""{chat.log or ""}\n\n"""
            previous_messages = [ {"role": "system", "content": system_prompt} ]
            openai_role = "user"
            prompt = user_prompt

            result, tokens_used = openai_call(prompt,role=openai_role, max_tokens=2000, previous_messages=previous_messages)
            print(result)
            print(f"TOKEN USED {tokens_used}")
            if result is False:
                # Summarize chat so far.
                chat.summarize_and_save()
                summary=True
            else:
                chat.log += f"{role.name}: {result}\n\n"
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

