from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import *


class DashboardLogin(APIView):
    def post(self, request):
        get_user = request.data.get("username")
        password = request.data.get("password")
        cond = Q(username=get_user) | Q(email=get_user)
        username = User.objects.filter(cond).first() # None, get error 

        if not username:
            data = {"User": False, "msg": "Invalid Username"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request, username=username.username, password=password)

        if not user:
            data = {"User": False, "msg": "Invalid Password"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if user is not None:
            try:
                Token.objects.create(user=user)
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.get(user=user)

            data = {
                "user": True,
                "token": str(token),
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {"User": False, "msg": "Invalid password"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token = Token.objects.get(user=request.user) #request.user = login user
        token.delete()
        data = {"status": "You Are Successfully Logout"}
        return Response(data, status=status.HTTP_200_OK)


class AssignedTask(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        users = User.objects.all()
        tasks = Task.objects.all()

        if users.count() < 1 or tasks.count() < users.count():
            return Response(
                {"error": "Not enough users or tasks to perform assignment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate the average number of assignments per task
        avg_assignments_per_task = AssignedTasks.objects.count() / tasks.count()

        for user in users:
            # Check if the user already has an assigned task
            if AssignedTasks.objects.filter(user=user).exists():
                print(f"User {user.username} already has an assigned task, skipping...")
                continue

            # Find the first unassigned task
            task = (
                tasks.exclude(assignedtasks__user=user)
                .annotate(num_assignments=models.Count("assignedtasks"))
                .filter(num_assignments__lt=avg_assignments_per_task)
                .first()
            )
            print(task)

            # Check if a task is found
            if task:
                print(f"Assigning task '{task.title}' to user {user.username}")
                # Assign the task to the user
                AssignedTasks.objects.create(user=user, task=task)
            else:
                print(
                    f"No task found with fewer assignments than average for user {user.username}"
                )

        return Response(
            {"message": "Tasks assigned successfully"}, status=status.HTTP_200_OK
        )
