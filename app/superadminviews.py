from django.shortcuts import render
from django.db.models import Q
from .models import Task, UserProfile, Adminusers
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


@login_required
def superadmin_dashboard(request):
    if not request.user.role == "superadmin":
        return redirect("dashboard")
    users_count = UserProfile.objects.filter(role="user").count()
    admins_count = UserProfile.objects.filter(role="admin").count()
    completed_tasks = Task.objects.filter(status="completed").count()
    pending_tasks = Task.objects.filter(status="pending").count()
    context = {
        "users_count": users_count,
        "admins_count": admins_count,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
    }
    return render(request, "superadmin/superadmindashboard.html", context)


@login_required
def superadmin_manage_users(request):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    user_admin_mappings = Adminusers.objects.select_related("user", "admin").all()
    assigned_users = user_admin_mappings.values_list("user", flat=True)
    user_admin = UserProfile.objects.filter(role="user").exclude(id__in=assigned_users)
    assigned_users_list = list(user_admin_mappings)
    unassigned_users_list = list(user_admin)
    combined_users = {
        user.id: user for user in assigned_users_list + unassigned_users_list
    }.values()
    print(combined_users)
    return render(request, "superadmin/manage_users.html", {"users": combined_users})


@login_required
def superadmin_manage_admins(request):
    if not request.user.role == "superadmin":
        return redirect("dashboard")
    admin = UserProfile.objects.filter(role="admin")
    return render(request, "superadmin/manage_admins.html", {"admins": admin})


@login_required
def superadmin_assign_user_to_admin(request):
    if request.user.role != "superadmin":
        return redirect("dashboard")

    if request.method == "POST":
        admin_id = request.POST.get("admin_id")
        user_ids = request.POST.getlist("user_ids")
        admin = UserProfile.objects.get(Q(id=admin_id) & Q(role="admin"))
        try:
            for user_id in user_ids:
                user = UserProfile.objects.get(Q(id=user_id) & Q(role="user"))
                if not Adminusers.objects.filter(admin=admin, user=user).exists():
                    Adminusers.objects.create(admin=admin, user=user)
                else:
                    messages.error(
                        request, f"User {user.email} is already assigned to this admin."
                    )
                    return redirect("superadmin_assign_user_to_admin")

            messages.success(
                request, "Users have been successfully assigned to the admin."
            )
            return redirect("superadmin_assign_user_to_admin")

        except Exception as e:

            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("superadmin_assign_user_to_admin")

    admins = UserProfile.objects.filter(role="admin")
    users = UserProfile.objects.filter(role="user")
    return render(
        request,
        "superadmin/assign_user_to_admin.html",
        {
            "admins": admins,
            "users": users,
        },
    )


@login_required
def superadmin_manage_tasks(request):
    if not request.user.role == "superadmin":
        return redirect("dashboard")
    reports = Task.objects.all()
    return render(request, "superadmin/manage_tasks.html", {"reports": reports})


@login_required
def create_admin(request):
    if request.user.role != "superadmin":
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")
        name = request.POST.get("name")
        UserProfile.objects.create_user(
            email=email,
            name=name,
            mobile_number=mobile_number,
            password=password,
            role="admin",
        )
        return redirect("superadmin_manage_admins")
    return render(request, "superadmin/createadmin.html")


@login_required
def create_user(request):
    if request.user.role != "superadmin":
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")
        name = request.POST.get("name")
        UserProfile.objects.create_user(
            email=email,
            name=name,
            mobile_number=mobile_number,
            password=password,
            role="user",
        )
        return redirect("superadmin_manage_users")
    return render(request, "superadmin/createuser.html")


@login_required
def edit_admin(request, admin_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    admin = UserProfile.objects.get(id=admin_id)
    if request.method == "POST":
        admin.name = request.POST.get("name")
        admin.email = request.POST.get("email")
        admin.mobile_number = request.POST.get("mobile_number")
        new_role = request.POST.get("role")
        if new_role in ["admin","user"]:
            admin.role = new_role
        admin.save()
        return redirect("superadmin_manage_admins")
    return render(request, "superadmin/editadmin.html", {"admin": admin})
@login_required
def edit_user(request, user_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    user = UserProfile.objects.get(Q(id=user_id) & Q(role="user"))
    try:
        current_assignment = Adminusers.objects.get(user=user)
    except Adminusers.DoesNotExist:
        current_assignment = None
    admins = UserProfile.objects.filter(role="admin")

    if request.method == "POST":
        new_role = request.POST.get("role")
        if new_role and user.role != new_role and new_role != "user":
            if current_assignment:
                current_assignment.delete()
            
        user.name = request.POST.get("name")
        user.email = request.POST.get("email")
        user.mobile_number = request.POST.get("mobile_number")
        if new_role:
            user.role = new_role
        user.save()
        if user.role == "user":
            new_admin_id = request.POST.get("admin_id")
            if new_admin_id:
                new_admin = UserProfile.objects.get(id=new_admin_id, role="admin")
                Adminusers.objects.filter(user=user).delete()
                Adminusers.objects.create(user=user, admin=new_admin)
        return redirect("superadmin_manage_users")
    return render(
        request,
        "superadmin/edituser.html",
        {
            "user": user,
            "admins": admins,
            "current_admin": current_assignment.admin.id if current_assignment else None,
        },
    )
@login_required
def delete_user(request, user_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    admin = UserProfile.objects.get(Q(id=user_id) & Q(role="user"))
    admin.delete()
    return redirect("superadmin_manage_users")


@login_required
def delete_admin(request, admin_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    admin = UserProfile.objects.get(Q(id=admin_id) & Q(role="admin"))
    admin.delete()
    return redirect("superadmin_manage_admins")


@login_required
def view_task(request, task_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    task = Task.objects.get(id=task_id)
    return render(request, "superadmin/viewtask.html", {"task": task})


@login_required
def edit_task(request, task_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        assigned_to_id = request.POST.get("assigned_to")
        if assigned_to_id:
            assigned_user = UserProfile.objects.get(id=assigned_to_id, role="user")
            task.assigned_to = assigned_user
            task.save()
            messages.success(request, "Task updated successfully.")
            return redirect("view_task", task_id=task.id)
        else:
            messages.error(request, "Please select a valid user.")
    users = UserProfile.objects.filter(role="user")
    return render(request, "superadmin/edittask.html", {"task": task, "users": users})


@login_required
def delete_task(request, task_id):
    if request.user.role != "superadmin":
        return redirect("dashboard")

    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect("superadmin_manage_tasks")
