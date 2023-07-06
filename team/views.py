from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf import settings
from django.urls import reverse

from team.models import Team, Chat
from team.ai import openai_call, openai_image
from team.utils import approximate_word_count
from team import prompts

import urllib.parse
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
    mascfem = request.GET.get('mascfem', random.choice(["male", "female"]))
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
    sample_size = 200

    template_context["recent"] = Team.objects.filter(private=False).order_by('-created')[:sample_size]
    try:
        pks = random.sample([val for val in Team.objects.filter(private=False).values_list('pk', flat=True)], sample_size)
    except ValueError:
        pks = [val for val in Team.objects.filter(private=False).values_list('pk', flat=True)]

    template_context["random"] = Team.objects.filter(pk__in=pks)
    response = TemplateResponse(request, "home.html", template_context)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response["Pragma"] = "no-cache" # HTTP 1.0.
    response["Expires"] = "0" # Proxies.
    return response

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
    template_context = {}
    try:
        chat = Chat.objects.get(guid=guid)
    except:
        chat = None

    if not chat:
        return TemplateResponse(request, "chat.html", {})

    brand_new_chat=False
    if not chat.log and not chat.log_historical:
        brand_new_chat=True
        initial_chat_log = f"""# CHAT LOG - TEAM OBJECTIVE = {chat.team.objective}

## Moderator
Team, begin work on your objective. Good luck.

"""
        chat.log = initial_chat_log
        chat.next_role_name = chat.team.role_set.all()[0].name
        print(f"brand new chat, first role name = {chat.next_role_name}")
        chat.save()
    
    human_input = request.POST.get('human_input', None)
    human_role_name = request.POST.get('human_role_name', None)
    if human_input and human_role_name:
        new_log_item = f"\n\n## {human_role_name}\n{human_input}\n\n"
        print(f"Human input. new log item: {new_log_item}")
        chat.log += f"\n\n## {human_role_name}\n{human_input}\n\n"

        next_role_name = chat.team.role_set.all()[0].name
        role_list = []
        for role in chat.team.role_set.all():
            role_list.append(role)
        print(f"role list is {role_list} - time to find the moderator that comes next")
        for idx, role in enumerate(role_list):
            if role.name == human_role_name:
                try:
                    next_role_name = role_list[idx+1].name
                except:
                    next_role_name = role_list[0].name
                print(f"is the human {role.name} so next is: {next_role_name}")
                break
            print(f"not human: {role.name}")

        print(f"Next up is {next_role_name}") 
        chat.next_speaker_name = next_role_name
        chat.save()
        return HttpResponseRedirect(reverse('chat-by-guid', args=(guid,)))



    # find next human speaker name & give it to template
    possible_human_names = chat.human_roles.all().values_list('name', flat=True)
    if len(possible_human_names) == 0:
        next_human_role_name = "Human Moderator"
    elif len(possible_human_names) == 1:
        next_human_role_name = possible_human_names[0]
    else:
        role_list = []
        for role in chat.team.role_set.all():
            role_list.append(role)
        for idx, role in enumerate(role_list):
            # move through the order until the next speaker,
            # then find the next human speaker
            if role is None:
                continue 
            if role.name != chat.next_speaker_name:
                seen_next_speaker=True
                continue

            if seen_next_speaker and chat.next_speaker_name in possible_human_names:
                next_human_role_name = chat.next_speaker_name
                break
            
        if not next_human_role_name:
            next_human_role_name = possible_human_names[0]

    print(f"Next human role: {next_human_role_name}")
    template_context["human_role_name"] = next_human_role_name
    template_context["chat"] = chat
    return TemplateResponse(request, "chat.html", template_context)

