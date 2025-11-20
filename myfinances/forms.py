# forms.py
from django import forms
from .models import Item
from django import forms
from .models import Statements, Categories


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'quantity']

class StatementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get unique Groups manually
        seen_groups = set()
        unique_categories = []
        for cat in Categories.objects.order_by("Group"):
            if cat.Group not in seen_groups:
                unique_categories.append(cat)
                seen_groups.add(cat.Group)

        self.fields["Category"].queryset = Categories.objects.filter(id__in=[c.id for c in unique_categories])

    class Meta:
        model = Statements
        fields = ["Category"]
