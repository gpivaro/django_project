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
    Group = forms.ChoiceField(label="Category Group", required=False)

    class Meta:
        model = Statements
        fields = []  # exclude Category from direct editing

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        # Build unique group choices
        groups = (
            Categories.objects
            .order_by("Group")
            .values_list("Group", flat=True)
            .distinct()
        )
        self.fields["Group"].choices = [(g, g) for g in groups]

        # Pre-fill the current group if instance has a category
        if instance and instance.Category:
            self.fields["Group"].initial = instance.Category.Group



