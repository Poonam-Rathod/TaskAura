from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

PRIORITY_CHOICES = [
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
]

CATEGORY_CHOICES = [
    ('Work', 'Work'),
    ('Personal', 'Personal'),
    ('Study', 'Study'),
    ('Other', 'Other'),
]

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Other')
    is_deleted = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')

    def is_overdue(self):
        if self.due_date and not self.completed:
            return timezone.localdate() > self.due_date
        return False

    def __str__(self):
        return f"{self.title} ({self.priority})"


# ------------------ Focus Mode ------------------

class FocusSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    def calculate_duration(self):
        if self.end_time:
            self.duration_minutes = int((self.end_time - self.start_time).total_seconds() // 60)
            self.save()

    def __str__(self):
        if self.task:
            return f"Focus: {self.task.title} - {self.duration_minutes} min"
        return f"Focus session - {self.duration_minutes} min"
