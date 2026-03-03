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
