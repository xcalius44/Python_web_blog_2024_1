from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("user", "recipe")

# Custom manager
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.PUBLISHED)

# Recipe model
class Recipe(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    ingredients = models.TextField()
    instructions = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status, default=Status.DRAFT)
    
    saved_by = models.ManyToManyField(User, related_name="saved_recipes", blank=True)
    rating = models.FloatField(default=0, help_text="Average rating")
    rating_count = models.IntegerField(default=0, help_text="Number of ratings")
    calories = models.IntegerField(null=True, blank=True, help_text="Calories per serving")
    cooking_time = models.IntegerField(null=True, blank=True, help_text="Cooking time in minutes")
    popularity = models.IntegerField(default=0, help_text="Used for ordering popular recipes")

    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class Meta:
        ordering = ['-publish']
        indexes = [models.Index(fields=['-publish'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "recipes:recipe_detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug]
        )

# Comment model (optional, can be disabled later)
class Comment(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80, verbose_name="Ім'я")
    email = models.EmailField()
    body = models.TextField(verbose_name="Текст коментаря")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created'])]

    def __str__(self):
        return f"Comment by {self.name} on {self.recipe}"
