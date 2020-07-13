from django.urls import path
from monitoring import views

urlpatterns = [
    path('agents/<str:agent_ip>', views.AgentDetailView.as_view()),
    path('agents', views.AgentListCreateView.as_view()),
    path('endpoints/<str:endpoint_uuid>', views.EndpointDetailView.as_view()),
    path('endpoints', views.EndpointListCreateView.as_view()),
    path('groups', views.GroupListCreateView.as_view())
]
