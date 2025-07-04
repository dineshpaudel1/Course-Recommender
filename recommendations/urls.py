from django.urls import path
from .views.courses_view import *
from .views.user_view import *
from django.conf import settings
from django.conf.urls.static import static
from recommendations.views import admin_view

urlpatterns = [
    path('', home_view, name='home'),
    path('search/', search_view, name='search'),
    path('course/<int:course_id>/', course_detail_view, name='course_detail'),
    path('instructor/<int:instructor_id>/courses/', instructor_courses_view, name='instructor_courses'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path("admin/login/",  admin_view.admin_login,  name="admin_login"),
    path("admin/logout/", admin_view.admin_logout, name="admin_logout"),
    path("admin/",  admin_view.admin_dashboard,  name="admin_dashboard"),
    path("admin/courses/", admin_view.admin_courses, name="admin_courses"),
    path("admin/users/", admin_view.admin_users, name="admin_users"),
    path("admin/search/", admin_view.admin_search, name="admin_search"),
    path("admin/courses/<int:id>/", admin_view.admin_course_detail, name="admin_course_details"),
    path("courses/<int:pk>/delete/", admin_view.admin_course_delete, name="admin_course_delete"),
    path("courses/<int:pk>/edit/", admin_view.admin_course_edit, name="admin_course_edit"), 
    path("instructors/", admin_view.admin_instructors, name="admin_instructors"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
