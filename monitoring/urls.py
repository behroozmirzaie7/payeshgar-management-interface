from django.urls import path
from monitoring import views


urlpatterns = [
    path('agents/<str:agent_name>', views.AgentDetailView.as_view()),
    path('agents', views.AgentListCreateView.as_view()),
]
