# forms.py
from django import forms
from .models import Item
from django import forms
from .models import Statements, CategoryList


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'quantity']


class StatementForm(forms.ModelForm):
    Name = forms.ChoiceField(label="Category", required=False)

    class Meta:
        model = Statements
        fields = []  # exclude Category from direct editing

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        # Build unique group choices
        names = (
            CategoryList.objects
            .order_by("name")
            .values_list("name", flat=True)
            .distinct()
        )
        self.fields["Name"].choices = [(g, g) for g in names]

        # Pre-fill the current group if instance has a category
        if instance and instance.Category:
            self.fields["Name"].initial = instance.Category.name
