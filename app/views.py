from django.shortcuts import render
from .permission import IsAdmin,IsSuperAdmin,IsUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import AllowAny
from .models import Task,UserProfile,Adminusers
from .serializer import TaskDetailsGettingSerializer,TaskDetailsEdittingSerializer,TaskDetailsAdminSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.views import LogoutView
# Create your views here.
from rest_framework_simplejwt.tokens import RefreshToken
class UserGettingTasks(APIView):
    permission_classes = [IsUser]

    def get(self, request):
        user = request.user
        alltasks = Task.objects.filter(assigned_to=user)

        if not alltasks:
            return Response("Invalid")
        else:
            # Use the correct serializer here
            serializer = TaskDetailsGettingSerializer(
                alltasks, many=True, context={"request": request}
            )
            return Response(serializer.data)
class Register_Super_admin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        mobile_number = request.data.get("mobile_number")
        name = request.data.get("name")

        if not all([email, password, mobile_number, name]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.create_superadmin(
                email=email,
                password=password,
                mobile_number=mobile_number,
                name=name
            )
            return Response({"message": "Registered Successfully"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Login_Email_and_Password(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)

        if user is not None:

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response(
                {
                    "access": access_token,
                    "refresh": str(refresh)
                }
            )
        else:

            return Response(
                {"error": "invaliduser"}, status=status.HTTP_401_UNAUTHORIZED
            )


class Taskeditting(APIView):
    permission_classes = [IsUser]

    def put(self, request, id):
        user = request.user
        task = Task.objects.get(Q(assigned_to=user) & Q(id=id))
        if not task:
            return Response({"detail": "Task not found "}, 
                            status=status.HTTP_404_NOT_FOUND)
        serializer = TaskDetailsEdittingSerializer(task, data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get("status") == "completed":
                if not serializer.validated_data.get("completion_report") or serializer.validated_data.get("worked_hours") is None:
                    return Response({
                        "detail": "Both 'completion_report' and 'worked_hours' are required when marking the task as completed."
                    }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"detail": "Task updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AdminGettingTasks(APIView):
    permission_classes = [IsAdmin|IsSuperAdmin]

    def get(self, request,id):
        alltasks = Task.objects.get(Q(id=id)&Q(status="completed"))
        if not alltasks:
            return Response("Invalid")
        else:
            # Use the correct serializer here
            serializer = TaskDetailsAdminSerializer(
                alltasks, context={"request": request}
            )
            return Response(serializer.data)

def dashboard(request):
    return render(request, 'user/dashboard.html')

# ---------- ADMIN VIEWS ----------

@login_required
def admin_task_reports(request):
    if not request.user.role=="admin" :
        return redirect('dashboard')
    managed_users = Adminusers.objects.filter(admin=request.user).values_list('user', flat=True)

    # Fetch tasks assigned to these users
    reports = Task.objects.filter(Q(assigned_to__in=managed_users) & Q(status="completed"))
    return render(request, 'admin/reports.html', {'reports': reports})

@login_required
def admindashboard(request):
    if not request.user.role=="admin":
        return redirect('dashboard')
    assigned_users_count = Adminusers.objects.filter(admin=request.user.id).count()

    # Assigned tasks: completed and pending for users assigned to the admin
    assigned_completed_tasks_count = Task.objects.filter(
        assigned_to__Users__admin=request.user.id, status="completed"
    ).count()

    assigned_pending_tasks_count = Task.objects.filter(
        assigned_to__Users__admin=request.user.id, status="pending"
    ).count()

    # Context to pass to the template
    context = {
        'users_count': assigned_users_count,
        'completed_tasks_count': assigned_completed_tasks_count,
        'pending_tasks_count': assigned_pending_tasks_count,
    }

    return render(request, 'admin/dashboard.html', context)

@login_required
def manage_users(request):
    if not request.user.role=="admin":
        return redirect('dashboard')
    users = Adminusers.objects.filter(admin__in=request.user).values_list('user', flat=True)
    return render(request, 'admin/users.html', {'users': users})

@login_required
def manage_tasks(request):
    if not request.user.role=="admin":
        return redirect('dashboard')
    tasks = Task.objects.filter(assigned_to__Users__admin=request.user.id)
    return render(request, 'admin/tasks.html', {'tasks': tasks})

# ---------- COMMON DASHBOARD ----------

@login_required
def dashboard(request):
    # redirect based on role
    if request.user.role=="superadmin":
        return redirect('superadmin_dashboard')
    elif request.user.role=="admin":
        return redirect('admindashboard')
    else:
        return render(request, 'user/dashboard.html')  # regular user
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to dashboard after login
            print(user.role)
            if user.role == 'superadmin':
                return redirect('superadmin_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')  # This should match the 'name' from urls.py
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

class CustomLogoutView(LogoutView):
    next_page = 'login_view'  # or your desired login URL
    http_method_names = ['get', 'post']
    def dispatch(self, request, *args, **kwargs):
        request.session.flush()  
        return redirect(self.next_page)

@login_required
def admin_edit_task(request, task_id):
    if request.user.role != "admin":
        return redirect('dashboard')

    task = Task.objects.get(id=task_id)
    print(task)
    # Get users assigned to this admin only
    admin_users = Adminusers.objects.filter(admin=request.user).values_list('user', flat=True)
    users = UserProfile.objects.filter(id__in=admin_users)

    if request.method == 'POST':
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            try:
                assigned_user = UserProfile.objects.get(id=assigned_to_id, role='user', id__in=admin_users)
                task.assigned_to = assigned_user
                task.save()
                messages.success(request, "Task updated successfully.")
                return redirect('manage_tasks')
            except UserProfile.DoesNotExist:
                messages.error(request, "Selected user is not valid or not assigned to you.")
        else:
            messages.error(request, "Please select a valid user.")

    return render(request, 'admin/edittask.html', {'task': task, 'users': users})


@login_required
def admin_assign_task_to_user(request):
    # Check if the logged-in user is a superadmin
    if request.user.role != "admin":
        return redirect('dashboard')  # Redirect to dashboard if not a superadmin

    # Process form submission
    assigned_user_ids = Adminusers.objects.filter(admin=request.user).values_list('user_id', flat=True)
    users = UserProfile.objects.filter(id__in=assigned_user_ids, role="user")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to_id = request.POST.get("user_id")
        due_date = request.POST.get("due_date")
        print(assigned_to_id)
        # Security check: make sure the user being assigned belongs to this admin
        user=UserProfile.objects.get(id=assigned_to_id)
        
        try:
            Task.objects.create(
                title=title,
                description=description,
                assigned_to=user,
                due_date=due_date,
            )
            messages.success(request, "Task assigned successfully.")
            return redirect('admin_assign_task_to_user')
        except Exception as e:
            messages.error(request, f"Error assigning task: {str(e)}")

    return render(request, "admin/assign_task_to_user.html", {"users": users})