from django.urls import path
from inspecting import views

urlpatterns = [
    path('inspections', views.InspectionListAPIView.as_view()),
    path('inspection-results', views.CreateInspectionResultsAPIView.as_view()),

]
