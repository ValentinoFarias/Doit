from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import FocusItem, Note, Task


# Create your views here.

def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')


@login_required
def todolist(request):
    if request.method == "POST":
        if "toggle_task" in request.POST:
            try:
                task_id = int(request.POST.get("toggle_task") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

            task = get_object_or_404(Task, id=task_id, user=request.user)
            task.is_completed = not task.is_completed
            task.save(update_fields=["is_completed", "updated_at"])
            return redirect("todolist")

        if "delete_task" in request.POST:
            try:
                task_id = int(request.POST.get("delete_task") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

            task = get_object_or_404(Task, id=task_id, user=request.user)
            task.delete()
            return redirect("todolist")

        if "add_task" in request.POST:
            title = (request.POST.get("new_task") or "").strip()
            if title:
                Task.objects.create(title=title, user=request.user)
            return redirect("todolist")

    tasks = Task.objects.filter(user=request.user)
    focus_items = FocusItem.objects.filter(user=request.user)
    notes = Note.objects.filter(user=request.user)

    context = {
        "tasks": tasks,
        "focus_items": focus_items,
        "notes": notes,
        "today": timezone.localdate().strftime("%Y-%m-%d"),
    }
    return render(request, "todolist.html", context)


@login_required
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect("todolist")