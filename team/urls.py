from django.urls import path
from django.views.generic import TemplateView
from .views import team, team_by_guid, test_generate_profile_image

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html")),
    path("team", team),
    path("team/<guid>.json", team_by_guid, {'format': 'json'}, name='team-by-guid-json'),
    path("team/<guid>", team_by_guid, name='team-by-guid'),
    path("test98123", test_generate_profile_image),
]
