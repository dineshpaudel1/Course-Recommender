# recommendations/views/admin_view.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from recommendations.decorators import admin_required
from recommendations.models import *
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from recommendations.forms import *

def admin_login(request):
    """
    Custom login page for the course-recommendation admin panel.
    • If already logged in as an admin -> kicks straight to dashboard.
    • POST: authenticates username & password.
    """
    # already authenticated & has admin profile → skip login
    if (
        request.user.is_authenticated
        and hasattr(request.user, "admin_profile")
        and request.user.admin_profile.is_active
    ):
        return redirect("recommendations:admin_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        allowed = (
            user is not None
            and hasattr(user, "admin_profile")
            and user.admin_profile.is_active
        )
        if allowed:
            login(request, user)
            next_url = request.GET.get("next") or reverse("admin_dashboard")
            return redirect(next_url)

        messages.error(request, "Invalid credentials or not an active admin.")

    # GET or failed POST
    return render(request, "adminpanel/login.html")


def admin_logout(request):
    logout(request)
    return redirect("recommendations:admin_login")

@admin_required
def admin_dashboard(request):
    ctx = {
        "course_count":     Course.objects.count(),
        "instructor_count": Instructor.objects.count(),
        "user_count":       User.objects.count(),
        "admin_name":       request.user.admin_profile.full_name or request.user.username,

        # NEW ADDITIONS 👇
        "popular_courses": Course.objects.annotate(
            view_count=Count("courseview")
        ).order_by("-view_count")[:5],

        "recent_users": User.objects.order_by("-date_joined")[:5],
    }
    return render(request, "adminpanel/dashboard.html", ctx)

@admin_required
def admin_courses(request):
    """
    Admin listing of all courses with optional pagination.
    """
    # 1️⃣  Query – newest first, bringing the instructor in one DB hit
    course_qs = Course.objects.select_related("instructor").order_by("-id")

    # 2️⃣  Pagination – 25 per page (change as needed)
    paginator = Paginator(course_qs, 25)
    page_number = request.GET.get("page")
    courses_page = paginator.get_page(page_number)   # returns Page object

    # 3️⃣  Render
    return render(
        request,
        "adminpanel/courses.html",
        {
            "courses": courses_page,   # <Page object> works fine in the template
        },
    )

@admin_required
def admin_users(request):
    """
    Admin list of all users + profile data, paginated.
    """
    qs = (
        User.objects
        .select_related("userprofile")              # 👈 1 DB hit for profile
        .order_by("-date_joined")                   # newest first
    )

    paginator   = Paginator(qs, 25)                 # 25 per page
    users_page  = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "adminpanel/users.html",
        {"users": users_page},
    )

@admin_required
def admin_instructors(request):
    qs = (
        Instructor.objects
        .annotate(course_total=Count("course"))   # 🔑 count related courses
        .order_by("name")
    )

    paginator   = Paginator(qs, 25)
    instructors = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "adminpanel/instructors.html",
        {"instructors": instructors},
    )

@admin_required
def admin_search(request):
    query = request.GET.get("q", "").strip()
    courses = Course.objects.filter(title__icontains=query) if query else []
    users   = User.objects.filter(username__icontains=query) if query else []

    context = {
        "query": query,
        "courses": courses,
        "users": users,
    }
    return render(request, "adminpanel/search_results.html", context)

@admin_required
def admin_course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, "adminpanel/course_details.html", {"course": course})

@admin_required
@require_POST                         # only allow POST (safer)
def admin_course_delete(request, pk):
    """
    Permanently deletes a course and returns to the list view.
    """
    course = get_object_or_404(Course, pk=pk)
    title = course.title              # store for the toast
    course.delete()
    messages.success(request, f"Course “{title}” was deleted.")
    return redirect("admin_courses")

@admin_required
def admin_course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        # Assign each field from POST — add .strip() where it makes sense
        course.title        = request.POST.get("title", "").strip()
        course.url          = request.POST.get("url", "").strip()
        course.thumbnail    = request.POST.get("thumbnail", "").strip()
        course.instructor_id = request.POST.get("instructor")
        course.num_lectures = request.POST.get("num_lectures") or 0
        course.subscribers  = request.POST.get("subscribers") or 0
        course.price        = request.POST.get("price", "").strip()
        course.currency     = request.POST.get("currency", "").strip()
        course.duration     = request.POST.get("duration", "").strip()
        course.rating       = request.POST.get("rating") or 0
        course.topic        = request.POST.get("topic", "").strip()
        course.description  = request.POST.get("description", "").strip()

        course.save()
        messages.success(request, "Course updated successfully.")
        return redirect("admin_course_details", id=pk)

    instructors = Instructor.objects.all().order_by("name")
    return render(
        request,
        "adminpanel/course_edit.html",
        {"course": course, "instructors": instructors},
    )