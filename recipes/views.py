from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST


from .forms import CommentForm
from .models import Recipe

# --- List view (paginated) ---
class RecipeListView(ListView):
    queryset = Recipe.published.all()
    context_object_name = 'recipes'
    paginate_by = 3
    template_name = 'recipes/recipe/list.html'


# --- Homepage (popular recipes) ---
def home(request):
    # Order by popularity field (integer you set in admin)
    popular_recipes = Recipe.published.order_by('-popularity')[:6]
    return render(request, 'recipes/home.html', {'popular_recipes': popular_recipes})


# --- Search view (keyword + tags) ---
def recipe_search(request):
    query = request.GET.get('q')
    recipes = Recipe.published.all()

    # Keyword search
    if query:
        recipes = recipes.filter(title__icontains=query)

    # Tag filters (checkboxes in template)
    selected_tags = request.GET.getlist('tags')
    if selected_tags:
        recipes = recipes.filter(tags__name__in=selected_tags).distinct()

    # Pass all tags to template so checkboxes can be generated dynamically
    all_tags = Tag.objects.all()

    return render(
        request,
        'recipes/recipe/search.html',
        {'recipes': recipes, 'query': query, 'all_tags': all_tags, 'selected_tags': selected_tags}
    )


# --- Recipe list (with optional tag filter) ---
def recipe_list(request, tag_slug=None):
    recipe_list = Recipe.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        recipe_list = recipe_list.filter(tags__in=[tag])

    paginator = Paginator(recipe_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        recipes = paginator.page(page_number)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        recipes = paginator.page(1)

    return render(request, 'recipes/recipe/list.html', {'recipes': recipes, 'tag': tag})


# --- Recipe detail ---
def recipe_detail(request, year, month, day, slug):
    recipe = get_object_or_404(
        Recipe,
        status=Recipe.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    tags = recipe.tags.all()
    recipe_tags_ids = recipe.tags.values_list('id', flat=True)
    similar_recipes = Recipe.published.filter(tags__in=recipe_tags_ids).exclude(id=recipe.id)
    similar_recipes = similar_recipes.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:3]

    # Handle comments
    comments = recipe.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.recipe = recipe
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request,
        'recipes/recipe/detail.html',
        {
            'recipe': recipe,
            'tags': tags,
            'similar_recipes': similar_recipes,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form
        }
    )


# --- Profile (saved recipes) ---
@login_required
def profile(request):
    saved = request.user.saved_recipes.all() if hasattr(request.user, 'saved_recipes') else []
    return render(request, 'recipes/profile.html', {'saved_recipes': saved})


# --- Dashboard (admin only) ---
@staff_member_required
def dashboard(request):
    return render(request, 'recipes/dashboard.html')

@require_POST
@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)
    rating_value = int(request.POST.get('rating', 0))
    if 1 <= rating_value <= 5:
        total = recipe.rating * recipe.rating_count
        recipe.rating_count += 1
        recipe.rating = (total + rating_value) / recipe.rating_count
        recipe.save()
    return redirect(recipe.get_absolute_url())
