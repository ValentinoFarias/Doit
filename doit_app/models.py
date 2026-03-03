from django.db import models

# Create your models here.


class Task(models.Model):
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
	title = models.TextField()
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.title


class Note(models.Model):
	content = models.TextField()
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.content[:50]
