from django.urls import path
from django.views.generic import TemplateView
from .views import team, team_by_guid, test_generate_profile_image, home, chat_by_guid, create_team_chat_by_guid, test_generate_any_image

urlpatterns = [
    path("", home),
    path("team/", team),
    path("team/<guid>.json", team_by_guid, {'format': 'json'}, name='team-by-guid-json'),
    path("team/<guid>/", team_by_guid, name='team-by-guid'),
    path("team/<team_guid>/chat/", create_team_chat_by_guid, name='create-team-chat-by-guid'),
    path("chat/<guid>/", chat_by_guid, name='chat-by-guid'),
    #path("test98123", test_generate_profile_image),
    #path("test110001", test_generate_any_image),
]
