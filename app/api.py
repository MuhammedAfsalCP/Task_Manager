
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from .views import (
    UserGettingTasks,
    Taskeditting,
    AdminGettingTasks,
)


urlpatterns = [
    path("api/user-login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/tasks/", UserGettingTasks.as_view()),
    path("api/tasks/<int:id>/", Taskeditting.as_view()),
    path("api/tasks/<int:id>/report/", AdminGettingTasks.as_view())
]
