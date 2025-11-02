from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, CATEGORY_CHOICES
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

# ------------------ PRIORITY & CATEGORY ------------------
PRIORITY_CHOICES = [
    ("High", "High"),
    ("Medium", "Medium"),
    ("Low", "Low"),
]

# ------------------ HOME / DASHBOARD ------------------
@login_required
def home(request):
    if request.method == "POST":
        title = request.POST.get("title")
        due_date = request.POST.get("due_date")
        category = request.POST.get("category") or "Other"
        priority = request.POST.get("priority") or "Medium"  # Default Medium

        if due_date == "":
            due_date = None

        if title:
            Task.objects.create(
                title=title,
                user=request.user,
                due_date=due_date,
                category=category,
                priority=priority
            )
            messages.success(request, "Task added successfully ✅")
        return redirect("home")

    tasks = Task.objects.filter(user=request.user, is_deleted=False).order_by("-created_at")
    total_tasks = tasks.count()
    completed_count = tasks.filter(completed=True).count()
    pending_count = tasks.filter(completed=False).count()
    today = timezone.localdate()

    # Progress %
    progress_percent = int((completed_count / total_tasks) * 100) if total_tasks else 0

    context = {
        "tasks": tasks,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
        "total_tasks": total_tasks,
        "progress_percent": progress_percent,
        "today": today,
        "categories": CATEGORY_CHOICES,
        "priorities": PRIORITY_CHOICES,  # For priority dropdown in form
    }

    return render(request, "tasks/home.html", context)


# ------------------ TASK CRUD ------------------
@login_required
def add_task(request):
    if request.method == "POST":
        title = request.POST.get("title")
        due_date = request.POST.get("due_date")
        category = request.POST.get("category") or "Other"
        priority = request.POST.get("priority") or "Medium"

        if due_date == "":
            due_date = None

        if title:
            Task.objects.create(
                title=title,
                user=request.user,
                due_date=due_date,
                category=category,
                priority=priority
            )
            messages.success(request, "Task added successfully ✅")
        return redirect("home")


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category") or "Other"
        priority = request.POST.get("priority") or "Medium"
        due_date = request.POST.get("due_date") or None

        if title:
            task.title = title
            task.category = category
            task.priority = priority
            task.due_date = due_date
            task.save()
            messages.success(request, "Task updated successfully ✏️")
            return redirect("home")

    context = {
        "task": task,
        "categories": CATEGORY_CHOICES,
        "priorities": PRIORITY_CHOICES,
    }
    return render(request, "tasks/edit_task.html", context)


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_deleted = True
    task.save()
    messages.success(request, "Task deleted (soft delete) ✅")
    return redirect("home")


@login_required
def restore_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user, is_deleted=True)
    task.is_deleted = False
    task.save()
    messages.success(request, "Task restored ✅")
    return redirect('deleted_tasks')


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user, is_deleted=False)
    task.completed = not task.completed
    task.save()

    # Recalculate progress
    tasks = Task.objects.filter(user=request.user, is_deleted=False)
    total = tasks.count()
    completed_count = tasks.filter(completed=True).count()
    progress_percent = int((completed_count / total) * 100) if total else 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'progress_percent': progress_percent})

    return redirect("home")


# ------------------ TASK FILTER VIEWS ------------------
@login_required
def pending_tasks_view(request):
    tasks = Task.objects.filter(user=request.user, completed=False)
    total = Task.objects.filter(user=request.user).count()
    completed_count = Task.objects.filter(user=request.user, completed=True).count()
    pending_count = total - completed_count

    context = {
        "tasks": tasks,
        "total_tasks": total,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
    }
    return render(request, "tasks/pending.html", context)


@login_required
def completed_tasks_view(request):
    tasks = Task.objects.filter(user=request.user, completed=True)
    total = Task.objects.filter(user=request.user).count()
    completed_count = tasks.count()
    pending_count = total - completed_count

    context = {
        "tasks": tasks,
        "total_tasks": total,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
    }
    return render(request, "tasks/completed.html", context)


@login_required
def deleted_tasks_view(request):
    tasks = Task.objects.filter(user=request.user, is_deleted=True)
    total = Task.objects.filter(user=request.user, is_deleted=False).count()
    completed_count = Task.objects.filter(user=request.user, completed=True, is_deleted=False).count()
    pending_count = total - completed_count
    deleted_count = tasks.count()

    context = {
        "tasks": tasks,
        "total_tasks": total,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
        "deleted_tasks": deleted_count,
    }
    return render(request, "tasks/deleted.html", context)


# ------------------ AUTHENTICATION ------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'tasks/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created! You can now login.")
            return redirect('login')
    return render(request, 'tasks/register.html')
@login_required
def undo_task(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id, user=request.user)
        if task.completed:
            task.completed = False
            task.save()
            messages.success(request, f"Task '{task.title}' marked as pending.")
    return redirect('home')

def focus_mode(request):
    tasks = Task.objects.filter(user=request.user, completed=False, is_deleted=False).order_by('priority')
    return render(request, 'tasks/focus_mode.html', {'tasks': tasks})

