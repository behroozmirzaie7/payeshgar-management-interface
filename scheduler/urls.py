from django.urls import path
from scheduler import views


urlpatterns = [
    path('inspections/<str:inspection_uuid>', views.InspectionDetailAPIView.as_view()),
    path('inspections', views.InspectionListAPIView.as_view()),

]
