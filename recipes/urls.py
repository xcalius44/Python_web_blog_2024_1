from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'), 
    path('list/', views.recipe_list), 
    path('recipes/', views.recipe_list, name='recipe_list'), 
    path('tag/<slug:tag_slug>/', views.recipe_list, name='recipe_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('search/', views.recipe_search, name='recipe_search'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
]