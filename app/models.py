from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, mobile_number, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin(self, email, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, mobile_number, password, **extra_fields)

    def create_superuser(self, email, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, mobile_number, password, **extra_fields)

class UserProfile(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=10, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile_number"]

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    @property
    def is_user(self):
        return self.role == 'user'

class Adminusers(models.Model):
    admin = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='admin',
        limit_choices_to={'role': 'admin'}
    )
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='Users',
        limit_choices_to={'role': 'user'}
    )

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role': 'user'}
    )
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
