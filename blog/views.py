import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Post
from analyticsapp.utils import get_client_ip

# Create your views here.
def home(request):
    get_client_ip(request, True)
    # key name posts will be accessible from the .html
    context = {"posts": Post.objects.all()}
    return render(request, "blog/home.html", context)


class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    ordering = ["-date_posted"]  # query database
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = "blog/user_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/blog/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    get_client_ip(request, True)
    return render(request, "blog/about.html", {"title": "About"})


# Views that will allow to pass database data to the javascript
# application that will handle some plots
def analytics(request):
    data = []
    label = []
    num_post = []
    week_posts = []
    week_legend = []

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    # loop for return number of posts by month
    for x in range(1, 12):
        start_date = datetime.date(2020, x, 1)
        end_date = datetime.date(2020, x + 1, 1)
        num_post.append(
            len(Post.objects.filter(date_posted__range=(start_date, end_date)))
        )
    return render(
        request,
        "blog/analytics.html",
        {
            "title": "Analytics",
            "num_post": num_post,
            "months": months,
            "week_posts": week_posts,
            "week_legend": week_legend,
        },
    )
