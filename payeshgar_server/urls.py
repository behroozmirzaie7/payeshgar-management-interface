from django.urls import path, include

urlpatterns = [
    path('api/v1/monitoring/', include('monitoring.urls')),
    path('api/v1/scheduler/', include('scheduler.urls')),
]
