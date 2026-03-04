from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
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
    editing_task_id = None
    if request.method == "POST":
        if "save" in request.POST:
            focus_content = request.POST.get("focus_content", "")
            notes_content = request.POST.get("notes_content", "")

            focus_text = focus_content.strip()
            FocusItem.objects.filter(user=request.user).delete()
            if focus_text:
                FocusItem.objects.create(user=request.user, title=focus_text)

            notes_text = notes_content.strip()
            Note.objects.filter(user=request.user).delete()
            if notes_text:
                Note.objects.create(user=request.user, content=notes_text)

            return redirect("todolist")

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

        if "start_edit" in request.POST:
            try:
                editing_task_id = int(request.POST.get("start_edit") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

        if "edit_task" in request.POST:
            try:
                task_id = int(request.POST.get("edit_task") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

            task = get_object_or_404(Task, id=task_id, user=request.user)
            new_title = (request.POST.get("edit_task_title") or "").strip()
            if new_title:
                task.title = new_title
                task.save(update_fields=["title", "updated_at"])
            return redirect("todolist")

    tasks = Task.objects.filter(user=request.user)
    focus_items = FocusItem.objects.filter(user=request.user)
    notes = Note.objects.filter(user=request.user)

    context = {
        "tasks": tasks,
        "focus_items": focus_items,
        "notes": notes,
        "today": timezone.localdate().strftime("%Y-%m-%d"),
        "editing_task_id": editing_task_id,
    }
    return render(request, "todolist.html", context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})
