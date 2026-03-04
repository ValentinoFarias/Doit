from django.conf import settings
from django.db import models

# Create your models here.


class Task(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="tasks",
		null=True,
		blank=True,
	)
	title = models.CharField(max_length=255)
	is_completed = models.BooleanField(default=False)
	due_date = models.DateField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["is_completed", "-created_at"]

	def __str__(self) -> str:
		return self.title


class FocusItem(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="focus_items",
		null=True,
		blank=True,
	)
	title = models.TextField()
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.title


class Note(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="notes",
		null=True,
		blank=True,
	)
	content = models.TextField()
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.content[:50]


class ProjectFolder(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="project_folders",
	)
	name = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		unique_together = ("user", "name")

	def __str__(self) -> str:
		return self.name


class SavedList(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="saved_lists",
	)
	project_folder = models.ForeignKey(
		ProjectFolder,
		on_delete=models.SET_NULL,
		related_name="saved_lists",
		null=True,
		blank=True,
	)
	name = models.CharField(max_length=255)
	due_at = models.DateTimeField()
	focus_content = models.TextField(blank=True, default="")
	notes_content = models.TextField(blank=True, default="")
	total_tasks = models.PositiveIntegerField(default=0)
	completed_tasks = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return self.name


class SavedListTask(models.Model):
	saved_list = models.ForeignKey(
		SavedList,
		on_delete=models.CASCADE,
		related_name="items",
	)
	title = models.CharField(max_length=255)
	is_completed = models.BooleanField(default=False)
	due_date = models.DateField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["is_completed", "created_at"]

	def __str__(self) -> str:
		return self.title
