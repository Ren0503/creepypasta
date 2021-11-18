from django.urls import path
from core.views import story_views as views

urlpatterns = [

    path('', views.getStories, name="stories"),

    path('create/', views.createStory, name="story-create"),
    path('upload/', views.uploadImage, name="image-upload"),

    path('<str:pk>/reviews/', views.createStoryReview, name="create-review"),
    path('top/', views.getTopStories, name='top-stories'),
    path('<str:pk>/', views.getStory, name="story"),

    path('update/<str:pk>/', views.updateStory, name="story-update"),
    path('delete/<str:pk>/', views.deleteStory, name="story-delete"),
]