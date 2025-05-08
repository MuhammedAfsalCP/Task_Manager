
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from app.views import (
    UserGettingTasks,
    Taskeditting,
    AdminGettingTasks,
    Login_Email_and_Password,
    Register_Super_admin,
)


urlpatterns = [
    path("user-login/", Login_Email_and_Password.as_view()),
    path("register-superadmin/", Register_Super_admin.as_view()),
    path("tasks/", UserGettingTasks.as_view()),
    path("tasks/<int:id>/", Taskeditting.as_view()),
    path("tasks/<int:id>/report/", AdminGettingTasks.as_view())
]
