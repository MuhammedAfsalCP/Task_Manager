from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from django.contrib.auth import views as auth_views
from .views import (
    UserGettingTasks,
    Taskeditting,
    AdminGettingTasks,
    dashboard,
    admindashboard,
    manage_tasks,
    manage_users,
    admin_task_reports,
    login_view,
    CustomLogoutView,
    admin_edit_task,
    admin_assign_task_to_user,
)
from .superadminviews import (
    superadmin_manage_users,
    superadmin_manage_admins,
    superadmin_manage_tasks,
    superadmin_assign_user_to_admin,
    create_admin,
    edit_admin,
    delete_admin,
    edit_user,
    delete_user,
    create_user,
    view_task,
    edit_task,
    superadmin_dashboard,
    delete_task,
)

urlpatterns = [
    path("admindashboard/", admindashboard, name="admin_dashboard"),
    path("superadmindashboard/", superadmin_dashboard, name="superadmin_dashboard"),
    path("dashboard/", dashboard, name="dashboard"),
    path("users/", manage_users, name="admin_manage_users"),
    path("superadminusers/", superadmin_manage_users, name="superadmin_manage_users"),
    path("superadmiadmins/", superadmin_manage_admins, name="superadmin_manage_admins"),
    path(
        "superadmiadminasignusers/",
        superadmin_assign_user_to_admin,
        name="superadmin_assign_user_to_admin",
    ),
    path(
        "superadminmanagetasks/",
        superadmin_manage_tasks,
        name="superadmin_manage_tasks",
    ),
    path(
        "superadmincreatadmin/",
        create_user,
        name="create_user",
    ),
    path(
        "superadmincreatuser/",
        create_admin,
        name="create_admin",
    ),
    path(
        "superadminviewtask/<int:task_id>/",
        view_task,
        name="view_task",
    ),
    path(
        "superadminedittask/<int:task_id>/",
        edit_task,
        name="edit_task",
    ),
    path(
        "adminedittask/<int:task_id>/",
        admin_edit_task,
        name="admin_edit_task",
    ),
    path(
        "superadmindeletetask/<int:task_id>/",
        delete_task,
        name="delete_task",
    ),
    path("superadmin/admins/edit/<int:admin_id>/", edit_admin, name="edit_admin"),
    path("superadmin/admins/delete/<int:admin_id>/", delete_admin, name="delete_admin"),
    path("superadmin/user/edit/<int:user_id>/", edit_user, name="edit_user"),
    path("superadmin/user/delete/<int:user_id>/", delete_user, name="delete_user"),
    path("tasks/", manage_tasks, name="manage_tasks"),
    path("reports/", admin_task_reports, name="admin_task_reports"),
    path(
        "adminassigntask/", admin_assign_task_to_user, name="admin_assign_task_to_user"
    ),
    path("", login_view, name="login_view"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
