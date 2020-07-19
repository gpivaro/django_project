from django.shortcuts import render


def home(request):
    return render(request, "resumesite/home.html", {})


def willcar(request):
    return render(request, "resumesite/willcar.html", {})


def git(request):
    return render(request, "resumesite/git.html", {})


posts = [
    {
        "author": "CoreyMS",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "August 27, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "August 28, 2018",
    },
]


def index(request):
    context = {"posts": posts}
    return render(request, "resumesite/index.html", context)

