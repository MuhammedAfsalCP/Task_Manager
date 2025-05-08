from rest_framework import serializers
from .models import UserProfile,Task


class TaskDetailsGettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
           "title",
           "description",
           "due_date",
           "status"
        )
        

class TaskDetailsEdittingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
           "status",
           "completion_report",
           "worked_hours"
        )

class TaskDetailsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
           "completion_report",
           "worked_hours"
        )