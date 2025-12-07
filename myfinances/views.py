from django.db.models.functions import TruncMonth
from .models import Statements, CategoryList
from django.db.models import Sum, Count
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Statements
from django.utils.timezone import now
from django.shortcuts import render
from django.utils.dateparse import parse_date
import csv
import io
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Categories, Users, Item, Statements, CategoryList
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from .utils import label_transactions, banktransactions_upload
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .forms import ItemForm, StatementForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.db.models import Sum


# To create API using rest framework
from rest_framework import viewsets
from .serializers import CategoriesSerializer, UsersSerializer


# Using rest framework out of the box view that handles CRUD
class CategoriesView(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


# Using rest framework out of the box view that handles CRUD
class UsersView(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer


# Create your views here.


# one parameter named request
def home(request):
    if request.method == "POST":
        return HttpResponseRedirect(reverse("myfinances:statement"))
    #     form = UserRegisterForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         username = form.cleaned_data.get("username")
    #         messages.success(
    #             request, f"Your account has been created! You are able to login."
    #         )
    #         return redirect("login")
    # else:
    #     form = UserRegisterForm()

    # return render(request, "users/register.html", {"form": form})
    return render(request, "myfinances/home.html")


# Return all available categories
@login_required
def categories(request):
    data = list(Categories.objects.order_by(
        "Group", "Expression").all().values())
    # return JsonResponse(data, safe=False)
    context = {"categories_list": Categories.objects.order_by("id").all()}
    return render(request, "myfinances/categories.html", context)
    # return JsonResponse(request, "myfinances/categories.html", context)


@login_required
# Main view of the application
# one parameter named request
def statement(request):
    # declaring template
    template = "myfinances/statement.html"
    data = Statements.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        "order": "Upload your statement file.",
        "statements": data,
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES["file"]

    # let's check if it is a csv file
    if csv_file.name.endswith(".CSV") or csv_file.name.endswith(".csv"):
        pass
    else:
        messages.error(request, "THIS IS NOT A CSV FILE")
    data_set = csv_file.read().decode("UTF-8")
    # setup a stream which is when we loop through each line we are able to handle a data in a stream

    io_string = io.StringIO(data_set)
    next(io_string)
    transactions_list = []
    for column in csv.reader(io_string, delimiter=","):

        transactions_list.append(
            {
                "Details": column[0],
                "Posting Date": column[1],
                "Description": column[2],
                "Amount": column[3],
                "Type": column[4],
                "Balance": column[5],
                "Check": column[6],
            }
        )

    # Query database for list of categories and convert to dataframe
    categories = Categories.objects.order_by(
        "Group", "Expression").all().values()
    categories_df = pd.DataFrame(categories)

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    # Call function to label the transactions
    labeled_transactions = label_transactions(
        transactions_list,
        categories_df,
        owner=request.user,   # ✅ pass authenticated user
        start_date=start_date,
        end_date=end_date
    )

    # Create a table row ID for table classification purpouses
    table_row_id = list(range(len(labeled_transactions["statement_dict"])))

    context = {
        "transactions_list": labeled_transactions["statement_dict"],
        "categories_list": labeled_transactions["categories_list"],
        "table_row_id": table_row_id,
        "categories_list": categories,
        "user_email": Users.objects.values_list('email', flat=True)
    }

    # If no table rows, then return the error message indication no data for the period selected
    if table_row_id:
        selected_end_date = labeled_transactions["statement_dict"][0]["Date"].strftime(
            "%m/%d/%Y"
        )
        selected_start_date = labeled_transactions["statement_dict"][
            len(labeled_transactions["statement_dict"]) - 1
        ]["Date"].strftime("%m/%d/%Y")

        messages.success(
            request,
            f"You have uploaded {csv_file} from {selected_start_date} to {selected_end_date}.",
        )
    else:
        messages.error(
            request, f"No data available for the period starting in {start_date}.",
        )

    return render(request, template, context)

# views.py


@login_required
def manage_items(request):
    ItemFormSet = modelformset_factory(Item, form=ItemForm, extra=0)
    if request.method == 'POST':
        formset = ItemFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            # No redirect — just re-render the same page
            return render(request, 'myfinances/item_table.html', {
                'formset': ItemFormSet(queryset=Item.objects.all()),
                'success': True
            })

    else:
        formset = ItemFormSet(queryset=Item.objects.all())
    return render(request, 'myfinances/item_table.html', {'formset': formset})


@login_required
def manage_statements(request):
    if request.method == "POST":
        stmt_id = request.POST.get("stmt_id")
        if stmt_id:
            try:
                # ✅ restrict lookup to current user's statements
                stmt = Statements.objects.get(pk=stmt_id, Owner=request.user)
            except Statements.DoesNotExist:
                return HttpResponse(status=404)

            form = StatementForm(request.POST, instance=stmt)
            if form.is_valid():
                # ✅ use Name instead of Group
                selected_name = form.cleaned_data["Name"]

                # find matching category by name
                matched_category = CategoryList.objects.filter(
                    name=selected_name
                ).first()

                stmt.Category = matched_category
                stmt.Owner = request.user   # already assigning ownership
                stmt.save()

                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return HttpResponse(status=204)  # No content
                else:
                    return redirect("myfinances:manage_statements")
        return HttpResponse(status=400)

    # ✅ only show statements owned by the current user
    user_statements = Statements.objects.filter(Owner=request.user)
    forms = [StatementForm(instance=stmt) for stmt in user_statements]
    return render(request, "myfinances/statement_table.html", {"forms": forms})


class CategoryListListView(LoginRequiredMixin, ListView):
    model = CategoryList
    template_name = 'myfinances/categorylist_list.html'
    context_object_name = 'categories_list'
    ordering = ['name', 'label']

    def get_queryset(self):
        qs = super().get_queryset()

        # Extract filters
        category_name = (self.request.GET.get("category_name") or "").strip()
        label = (self.request.GET.get("label") or "").strip()

        # Apply filters
        if category_name:
            qs = qs.filter(name__icontains=category_name)

        # Labels are exact values (choices), so filter by equality
        if label and label.lower() != "all":
            qs = qs.filter(label=label)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Build a unique, cleaned list of labels for the dropdown
        raw_labels = CategoryList.objects.values_list("label", flat=True)
        labels_unique = sorted(
            set(l.strip() for l in raw_labels if l and l.strip())
        )

        ctx["labels"] = labels_unique
        ctx["selected_name"] = (self.request.GET.get(
            "category_name") or "").strip()
        ctx["selected_label"] = (self.request.GET.get("label") or "").strip()

        return ctx


# Using Python Class Views to View Model. DetailView
class CategoryListDetailView(LoginRequiredMixin, DetailView):
    model = CategoryList


# Using Python Class Views to View Model. CreateView
class CategoryListCreateView(LoginRequiredMixin, CreateView):
    model = CategoryList
    fields = ['name', 'label']

    def form_valid(self, form):
        form.instance.owner = self.request.user

        try:
            return super().form_valid(form)
        except IntegrityError:
            # Add a user-friendly error to the form instead of crashing
            form.add_error(
                'name',
                "You already have a category with this name."
            )
            return self.form_invalid(form)


# Using Python Class Views to View Model. UpdateView
class CategoryListUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CategoryList
    fields = ['name', 'label']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError:
            # Add a user-friendly error to the form instead of crashing
            form.add_error(
                'name',
                "You already have a category with this name."
            )
            return self.form_invalid(form)

    def test_func(self):
        category = self.get_object()
        if self.request.user == category.owner:
            return True
        return False


# Using Python Class Views to View Model. DetailView
class CategoryListDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CategoryList
    success_url = reverse_lazy("myfinances:categories-list")

    def test_func(self):
        category = self.get_object()
        if self.request.user == category.owner:
            return True
        return False


@login_required
def banktransactions(request):
    """
    Handle the bank transactions upload view.

    Workflow:
    - On GET: render the upload page with a prompt message.
    - On POST: process the uploaded CSV file using `banktransactions_upload`,
      attach success/error messages via Django's messages framework,
      and re-render the page so the user sees feedback.

    Context:
    - `order`: instruction text displayed on the page.
    - `messages`: automatically injected by Django's messages framework
      (no need to pass explicitly).
    """

    # Template path
    template = "myfinances/banktransactions.html"

    # Context variable for instructions
    prompt = {
        "order": "Upload your bank transactions file.",
    }

    # GET request → show upload form
    if request.method == "GET":
        return render(request, template, prompt)

    # POST request → process file upload
    banktransactions_upload(request)

    # Re-render template with prompt (messages are auto-injected)
    return render(request, template, prompt)


# Using Python Class Views to View Model. Listview


class TransactionsListView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of Statement transactions for the logged-in user.

    Features:
    - Pagination with dynamic page size (?page_size=10|20|50|100|all).
    - Filtering by description (case-insensitive substring match).
    - Filtering by category (via CategoryList model).
    - Displays a total sum of the Amount column for the filtered queryset.
    - Exposes available categories for dropdown filtering in the template.
    """

    model = Statements
    template_name = 'myfinances/transactions_list.html'
    context_object_name = 'transactions'  # maps to object_list in template
    ordering = ['-Posting_Date']          # newest transactions first
    paginate_by = 20                      # default page size

    def get_paginate_by(self, queryset):
        """
        Determine pagination size based on ?page_size query parameter.

        Supported values:
        - 'all' → disables pagination (returns all results).
        - numeric values (e.g., 10, 20, 50, 100) → set per-page size.
        - defaults to self.paginate_by if not provided.

        Returns:
            int or None: number of items per page, or None to disable pagination.
        """
        page_size = self.request.GET.get("page_size")
        if page_size:
            if page_size.lower() == "all":
                return None  # disables pagination
            if page_size.isdigit():
                size = int(page_size)
                # clamp to reasonable bounds (1–500)
                return max(1, min(size, 500))
        return self.paginate_by

    def get_queryset(self):
        """
        Build the queryset of transactions for the current user.

        - Filters by Owner (logged-in user).
        - Orders by Posting_Date descending.
        - Applies optional filters:
          * description → case-insensitive substring match.
          * category → matches CategoryList.name unless 'all'.

        Returns:
            QuerySet: filtered and ordered transactions.
        """
        qs = super().get_queryset().filter(
            Owner=self.request.user).order_by(*self.ordering)

        # Filters
        description = self.request.GET.get("description")
        category = self.request.GET.get("category")

        if description:
            qs = qs.filter(Description__icontains=description)
        if category and category != "all":
            qs = qs.filter(Category__name=category)

        return qs

    def get_context_data(self, **kwargs):
        """
        Extend template context with additional data:

        - categories: all CategoryList entries for dropdown filter.
        - total_amount: sum of Amount column for filtered queryset.
        - current_page_size: reflects active page size selection
          (numeric or 'all') for template display.

        Returns:
            dict: context data for template rendering.
        """
        ctx = super().get_context_data(**kwargs)

        # Add a total to your context:
        qs = self.get_queryset()
        ctx["categories"] = CategoryList.objects.all()
        ctx["total_amount"] = qs.aggregate(total=Sum("Amount"))["total"] or 0

        # Expose current page size selection for the template
        page_size = self.request.GET.get("page_size")
        if not page_size:
            # reflect actual per_page when paginated, else 'all'
            if ctx.get('is_paginated'):
                page_size = str(ctx['paginator'].per_page)
            else:
                page_size = "all"
        ctx['current_page_size'] = page_size

        return ctx


# Using Python Class Views to View Model. DetailView
class TransactionsDetailView(LoginRequiredMixin, DetailView):
    model = Statements
    template_name = 'myfinances/transactions_detail.html'

# Using Python Class Views to View Model. UpdateView


class TransactionsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Statements
    fields = ['Category']
    template_name = 'myfinances/transactions_form.html'

    def test_func(self):
        transactions = self.get_object()
        if self.request.user == transactions.Owner:
            return True
        return False

# Using Python Class Views to View Model. DetailView


class TransactionsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Statements
    template_name = 'myfinances/transactions_confirm_delete.html'
    success_url = reverse_lazy("myfinances:transactions-list")

    def test_func(self):
        category = self.get_object()
        if self.request.user == category.Owner:
            return True
        return False


def balance_sheet(request):
    """
    Balance Sheet View

    - Accepts optional GET parameters: start_date, end_date, acct_info, category
    - If only start_date is provided, end_date defaults to today
    - Filters statements by Owner and optionally by Acct_Info and Category
    - Groups by Category and computes totals
    - Summarizes totals by label (Income, Expense, Asset, Liability, Equity, Other)
    - Provides grand total across all categories
    - Aggregates monthly totals by label for line chart visualization
    """

    # --- Step 1: Extract query parameters ---
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    acct_info = request.GET.get("acct_info")       # account filter
    category = request.GET.get("category")         # category filter

    # --- Step 2: Parse dates ---
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # --- Step 3: Default end_date to today if only start_date is provided ---
    if start_date and not end_date:
        end_date = now().date()

    # --- Step 4: Base queryset filtered by Owner ---
    qs = Statements.objects.filter(Owner=request.user)

    # --- Step 5: Filter by account if selected ---
    if acct_info:
        qs = qs.filter(Acct_Info=acct_info)

    # --- Step 6: Apply date filter ---
    if start_date and end_date:
        qs = qs.filter(Posting_Date__range=[start_date, end_date])

    # --- Step 7: Apply category filter ---
    if category and category != "all":
        qs = qs.filter(Category__name=category)

    # --- Step 8: Group by Category and compute totals ---
    category_totals = (
        qs.values("Category_id", "Category__name", "Category__label")
          .annotate(total_amount=Sum("Amount"))
          .order_by("Category__name")
    )

    # --- Step 9: Compute grand total ---
    grand_total = sum(row["total_amount"] or 0 for row in category_totals)

    # --- Step 10: Summarize by label ---
    label_summary = (
        qs.values("Category__label")
        .annotate(total_amount=Sum("Amount"))
        .order_by("-total_amount")
    )

    # --- Step 11: Monthly totals by label (for line chart) ---
    monthly_data = (
        qs.annotate(month=TruncMonth("Posting_Date"))
          .values("month", "Category__label")
          .annotate(total_amount=Sum("Amount"))
          .order_by("month", "Category__label")
    )

    # Reshape into dict: {label: {month: total}}
    chart_data = {}
    for row in monthly_data:
        month = row["month"].strftime("%Y-%m")
        label = row["Category__label"]
        chart_data.setdefault(label, {})[month] = float(
            row["total_amount"] or 0)

    # --- Step 12: Collect distinct accounts for dropdown ---
    acct_infos = (
        Statements.objects.filter(Owner=request.user)
        .values_list("Acct_Info", flat=True)
        .distinct()
    )
    acct_infos = sorted(set(acct.strip() for acct in acct_infos if acct))

    # --- Step 13: Collect distinct categories for dropdown ---
    categories = CategoryList.objects.all()

    # --- Step 14: Build context ---
    context = {
        "category_totals": category_totals,
        "grand_total": grand_total,
        "label_summary": label_summary,
        "chart_data": chart_data,   # <-- monthly totals by label
        "start_date": start_date_str,
        "end_date": end_date_str or str(end_date),
        "acct_infos": acct_infos,
        "selected_acct": acct_info,
        "categories": categories,
    }

    # --- Step 15: Render template ---
    return render(request, "myfinances/balance_sheet.html", context)


class LandingPageView(LoginRequiredMixin, TemplateView):
    template_name = "myfinances/landing.html"
    login_url = "login"        # redirect to your login view
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Statements.objects.filter(Owner=self.request.user)

        context["total_transactions"] = qs.count()
        context["uncategorized_count"] = qs.filter(
            Category__isnull=True).count()
        context["grand_total"] = qs.aggregate(
            total=Sum("Amount"))["total"] or 0
        context["category_count"] = qs.values("Category").distinct().count()
        return context
