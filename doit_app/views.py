from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import FocusItem, Note, Task


# Create your views here.

def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')


def todolist(request):
    if request.method == "POST":
        if "toggle_task" in request.POST:
            try:
                task_id = int(request.POST.get("toggle_task") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

            task = get_object_or_404(Task, id=task_id)
            task.is_completed = not task.is_completed
            task.save(update_fields=["is_completed", "updated_at"])
            return redirect("todolist")

        if "delete_task" in request.POST:
            try:
                task_id = int(request.POST.get("delete_task") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

            task = get_object_or_404(Task, id=task_id)
            task.delete()
            return redirect("todolist")

        if "add_task" in request.POST:
            title = (request.POST.get("new_task") or "").strip()
            if title:
                Task.objects.create(title=title)
            return redirect("todolist")

        if "save" in request.POST:
            if "completed_tasks" in request.POST:
                selected_ids_raw = request.POST.getlist("completed_tasks")
                selected_ids: list[int] = []
                for value in selected_ids_raw:
                    try:
                        selected_ids.append(int(value))
                    except (TypeError, ValueError):
                        continue

                Task.objects.exclude(id__in=selected_ids).update(is_completed=False)
                Task.objects.filter(id__in=selected_ids).update(is_completed=True)

            focus_content = request.POST.get("focus_content")
            if focus_content is not None:
                FocusItem.objects.all().delete()
                focus_text = focus_content.strip()
                if focus_text:
                    FocusItem.objects.create(title=focus_text)

            notes_content = request.POST.get("notes_content")
            if notes_content is not None:
                Note.objects.all().delete()
                notes_text = notes_content.strip()
                if notes_text:
                    Note.objects.create(content=notes_text)

            return redirect("todolist")

    tasks = Task.objects.all()
    focus_items = FocusItem.objects.all()
    notes = Note.objects.all()

    context = {
        "tasks": tasks,
        "focus_items": focus_items,
        "notes": notes,
        "today": timezone.localdate().strftime("%Y-%m-%d"),
    }
    return render(request, "todolist.html", context)


def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect("todolist")