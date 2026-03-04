from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import FocusItem, Note, ProjectFolder, SavedList, SavedListTask, Task


# Create your views here.

def index(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')


@login_required
def todolist(request):
    edit_task_id = None

    if request.method == "POST":
        if "save_list" in request.POST:
            list_name = (request.POST.get("list_name") or "").strip()
            due_raw = request.POST.get("list_due_at") or ""
            project_folder_id = request.POST.get("project_folder_id") or ""

            if not list_name or not due_raw:
                return redirect("todolist")

            try:
                due_at = datetime.fromisoformat(due_raw)
            except ValueError:
                return redirect("todolist")

            if timezone.is_naive(due_at):
                due_at = timezone.make_aware(due_at, timezone.get_current_timezone())

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

            user_tasks = Task.objects.filter(user=request.user)
            total_tasks = user_tasks.count()
            completed_tasks = user_tasks.filter(is_completed=True).count()

            project_folder = None
            if project_folder_id:
                try:
                    parsed_project_folder_id = int(project_folder_id)
                except (TypeError, ValueError):
                    parsed_project_folder_id = None

                if parsed_project_folder_id:
                    project_folder = get_object_or_404(ProjectFolder, id=parsed_project_folder_id, user=request.user)

            saved_list = SavedList.objects.create(
                user=request.user,
                project_folder=project_folder,
                name=list_name,
                due_at=due_at,
                focus_content=focus_text,
                notes_content=notes_text,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
            )

            SavedListTask.objects.bulk_create(
                [
                    SavedListTask(
                        saved_list=saved_list,
                        title=task.title,
                        is_completed=task.is_completed,
                        due_date=task.due_date,
                    )
                    for task in user_tasks
                ]
            )
            messages.success(request, "Saved list created successfully.")

            return redirect("dashboard")

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

        if "update_task" in request.POST:
            try:
                task_id = int(request.POST.get("update_task") or "")
            except (TypeError, ValueError):
                return redirect("todolist")

            title = (request.POST.get("edited_task_title") or "").strip()
            task = get_object_or_404(Task, id=task_id, user=request.user)
            if title:
                task.title = title
                task.save(update_fields=["title", "updated_at"])
            return redirect("todolist")

    raw_edit_task_id = request.GET.get("edit")
    if raw_edit_task_id:
        try:
            parsed_edit_task_id = int(raw_edit_task_id)
        except (TypeError, ValueError):
            parsed_edit_task_id = None

        if parsed_edit_task_id and Task.objects.filter(id=parsed_edit_task_id, user=request.user).exists():
            edit_task_id = parsed_edit_task_id

    tasks = Task.objects.filter(user=request.user)
    focus_items = FocusItem.objects.filter(user=request.user)
    notes = Note.objects.filter(user=request.user)
    project_folders = ProjectFolder.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    progress_percent = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    context = {
        "tasks": tasks,
        "focus_items": focus_items,
        "notes": notes,
        "project_folders": project_folders,
        "today": timezone.localdate().strftime("%Y-%m-%d"),
        "edit_task_id": edit_task_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "progress_percent": progress_percent,
    }
    return render(request, "todolist.html", context)


@login_required
def dashboard(request):
    active_filter = request.GET.get("filter", "today")
    valid_filters = {"notifications", "today", "upcoming", "someday", "completed", "inbox"}
    if active_filter not in valid_filters:
        active_filter = "today"
    if active_filter == "inbox":
        active_filter = "notifications"

    active_project_id = None
    raw_active_project = request.GET.get("project")
    if raw_active_project:
        try:
            parsed_project_id = int(raw_active_project)
        except (TypeError, ValueError):
            parsed_project_id = None

        if parsed_project_id and ProjectFolder.objects.filter(id=parsed_project_id, user=request.user).exists():
            active_project_id = parsed_project_id

    if request.method == "POST":
        if "create_project_folder" in request.POST:
            folder_name = (request.POST.get("project_folder_name") or "").strip()
            if folder_name:
                try:
                    ProjectFolder.objects.create(user=request.user, name=folder_name)
                    messages.success(request, "Project folder created successfully.")
                except IntegrityError:
                    messages.error(request, "A project folder with that name already exists.")
            return redirect("dashboard")

        if "update_project_folder" in request.POST:
            try:
                folder_id = int(request.POST.get("update_project_folder") or "")
            except (TypeError, ValueError):
                return redirect("dashboard")

            new_name = (request.POST.get("project_folder_new_name") or "").strip()
            folder = get_object_or_404(ProjectFolder, id=folder_id, user=request.user)
            if not new_name:
                messages.error(request, "Project folder name cannot be empty.")
                return redirect("dashboard")

            if ProjectFolder.objects.filter(user=request.user, name=new_name).exclude(id=folder_id).exists():
                messages.error(request, "A project folder with that name already exists.")
                return redirect("dashboard")

            folder.name = new_name
            folder.save(update_fields=["name", "updated_at"])
            messages.success(request, "Project folder updated successfully.")
            return redirect("dashboard")

        if "delete_project_folder" in request.POST:
            try:
                folder_id = int(request.POST.get("delete_project_folder") or "")
            except (TypeError, ValueError):
                return redirect("dashboard")

            folder = get_object_or_404(ProjectFolder, id=folder_id, user=request.user)
            folder.delete()
            messages.success(request, "Project folder deleted successfully.")
            return redirect("dashboard")

        if "delete_saved_list" in request.POST:
            try:
                saved_list_id = int(request.POST.get("delete_saved_list") or "")
            except (TypeError, ValueError):
                return redirect("dashboard")

            redirect_filter = request.POST.get("current_filter", active_filter)
            if redirect_filter not in valid_filters:
                redirect_filter = "today"
            if redirect_filter == "inbox":
                redirect_filter = "notifications"

            redirect_project_id = None
            raw_redirect_project = request.POST.get("current_project")
            if raw_redirect_project:
                try:
                    parsed_redirect_project = int(raw_redirect_project)
                except (TypeError, ValueError):
                    parsed_redirect_project = None

                if parsed_redirect_project and ProjectFolder.objects.filter(id=parsed_redirect_project, user=request.user).exists():
                    redirect_project_id = parsed_redirect_project

            saved_list = get_object_or_404(SavedList, id=saved_list_id, user=request.user)
            saved_list.delete()
            messages.success(request, "Saved list deleted successfully.")
            redirect_url = f"/dashboard/?filter={redirect_filter}"
            if redirect_project_id:
                redirect_url += f"&project={redirect_project_id}"
            return redirect(redirect_url)

        if "move_saved_list_folder" in request.POST:
            try:
                saved_list_id = int(request.POST.get("move_saved_list_folder") or "")
            except (TypeError, ValueError):
                return redirect("dashboard")

            redirect_filter = request.POST.get("current_filter", active_filter)
            if redirect_filter not in valid_filters:
                redirect_filter = "today"
            if redirect_filter == "inbox":
                redirect_filter = "notifications"

            redirect_project_id = None
            raw_redirect_project = request.POST.get("current_project")
            if raw_redirect_project:
                try:
                    parsed_redirect_project = int(raw_redirect_project)
                except (TypeError, ValueError):
                    parsed_redirect_project = None

                if parsed_redirect_project and ProjectFolder.objects.filter(id=parsed_redirect_project, user=request.user).exists():
                    redirect_project_id = parsed_redirect_project

            target_project_folder = None
            raw_target_folder_id = request.POST.get("target_project_folder") or ""
            if raw_target_folder_id:
                try:
                    parsed_target_folder_id = int(raw_target_folder_id)
                except (TypeError, ValueError):
                    parsed_target_folder_id = None

                if parsed_target_folder_id:
                    target_project_folder = get_object_or_404(ProjectFolder, id=parsed_target_folder_id, user=request.user)

            saved_list = get_object_or_404(SavedList, id=saved_list_id, user=request.user)
            saved_list.project_folder = target_project_folder
            saved_list.save(update_fields=["project_folder"])
            messages.success(request, "Saved list folder updated successfully.")

            redirect_url = f"/dashboard/?filter={redirect_filter}"
            if redirect_project_id:
                redirect_url += f"&project={redirect_project_id}"
            return redirect(redirect_url)

    all_saved_lists = SavedList.objects.filter(user=request.user)
    today_date = timezone.localdate()

    outstanding_tasks_count = Task.objects.filter(user=request.user, is_completed=False).count()
    notifications_lists = all_saved_lists.filter(due_at__date=today_date)
    notification_count = notifications_lists.count() + (1 if outstanding_tasks_count > 0 else 0)
    today_lists = all_saved_lists.filter(due_at__date=today_date)
    upcoming_lists = all_saved_lists.filter(due_at__date__gt=today_date)
    someday_lists = all_saved_lists.filter(due_at__date__gt=today_date + timedelta(days=30))
    completed_lists = all_saved_lists.filter(completed_tasks__gt=0, completed_tasks=F("total_tasks"))

    filtered_map = {
        "notifications": notifications_lists,
        "inbox": notifications_lists,
        "today": today_lists,
        "upcoming": upcoming_lists,
        "someday": someday_lists,
        "completed": completed_lists,
    }
    saved_lists = filtered_map[active_filter]

    if active_project_id:
        saved_lists = saved_lists.filter(project_folder_id=active_project_id)

    project_folders = ProjectFolder.objects.filter(user=request.user)

    context = {
        "saved_lists": saved_lists,
        "today": today_date,
        "active_filter": active_filter,
        "active_project_id": active_project_id,
        "notification_count": notification_count,
        "outstanding_tasks_count": outstanding_tasks_count,
        "notifications_due_today_count": notifications_lists.count(),
        "today_count": today_lists.count(),
        "upcoming_count": upcoming_lists.count(),
        "someday_count": someday_lists.count(),
        "completed_count": completed_lists.count(),
        "project_folders": project_folders,
    }
    return render(request, "dashboard.html", context)


@login_required
def saved_list_detail(request, list_id: int):
    saved_list = get_object_or_404(SavedList, id=list_id, user=request.user)

    def refresh_saved_list_counts() -> None:
        total_items = saved_list.items.count()
        completed_items = saved_list.items.filter(is_completed=True).count()
        saved_list.total_tasks = total_items
        saved_list.completed_tasks = completed_items
        saved_list.save(update_fields=["total_tasks", "completed_tasks"])

    edit_task_id = None

    if request.method == "POST":
        if "toggle_saved_task" in request.POST:
            try:
                item_id = int(request.POST.get("toggle_saved_task") or "")
            except (TypeError, ValueError):
                return redirect("saved_list_detail", list_id=list_id)

            item = get_object_or_404(SavedListTask, id=item_id, saved_list=saved_list)
            item.is_completed = not item.is_completed
            item.save(update_fields=["is_completed"])
            refresh_saved_list_counts()
            return redirect("saved_list_detail", list_id=list_id)

        if "delete_saved_task" in request.POST:
            try:
                item_id = int(request.POST.get("delete_saved_task") or "")
            except (TypeError, ValueError):
                return redirect("saved_list_detail", list_id=list_id)

            item = get_object_or_404(SavedListTask, id=item_id, saved_list=saved_list)
            item.delete()
            refresh_saved_list_counts()
            return redirect("saved_list_detail", list_id=list_id)

        if "add_saved_task" in request.POST:
            title = (request.POST.get("new_task") or "").strip()
            if title:
                SavedListTask.objects.create(saved_list=saved_list, title=title)
                refresh_saved_list_counts()
            return redirect("saved_list_detail", list_id=list_id)

        if "update_saved_task" in request.POST:
            try:
                item_id = int(request.POST.get("update_saved_task") or "")
            except (TypeError, ValueError):
                return redirect("saved_list_detail", list_id=list_id)

            title = (request.POST.get("edited_task_title") or "").strip()
            item = get_object_or_404(SavedListTask, id=item_id, saved_list=saved_list)
            if title:
                item.title = title
                item.save(update_fields=["title"])
            return redirect("saved_list_detail", list_id=list_id)

        if "update_saved_list" in request.POST:
            focus_text = (request.POST.get("focus_content") or "").strip()
            notes_text = (request.POST.get("notes_content") or "").strip()
            saved_list.focus_content = focus_text
            saved_list.notes_content = notes_text
            saved_list.save(update_fields=["focus_content", "notes_content"])
            messages.success(request, "Saved list updated successfully.")
            return redirect("saved_list_detail", list_id=list_id)

    raw_edit_task_id = request.GET.get("edit")
    if raw_edit_task_id:
        try:
            parsed_edit_task_id = int(raw_edit_task_id)
        except (TypeError, ValueError):
            parsed_edit_task_id = None

        if parsed_edit_task_id and saved_list.items.filter(id=parsed_edit_task_id).exists():
            edit_task_id = parsed_edit_task_id

    items = saved_list.items.all()
    total_tasks = items.count()
    completed_tasks = items.filter(is_completed=True).count()
    progress_percent = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    context = {
        "saved_list": saved_list,
        "tasks": items,
        "edit_task_id": edit_task_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "progress_percent": progress_percent,
        "today": timezone.localdate().strftime("%Y-%m-%d"),
    }
    return render(request, "saved_list_detail.html", context)


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
