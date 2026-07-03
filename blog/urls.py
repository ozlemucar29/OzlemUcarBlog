from django.urls import path
from . import views

urlpatterns = [
    # Blog list, about, contact
    path('', views.post_list, name='post_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Auth views
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    
    # Post CRUD views (must be defined BEFORE post detail to prevent slug collision with 'new')
    path('post/new/', views.post_create, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_update, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    
    # Comment Actions
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    # User Profile
    path('profile/', views.profile_edit, name='profile'),
    
    # Post Approve
    path('post/<slug:slug>/approve/', views.post_approve, name='post_approve'),
    path('post/<slug:slug>/reject/', views.post_reject, name='post_reject'),
    
    # Post detail view (catch-all for post/<slug>/)
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
]
