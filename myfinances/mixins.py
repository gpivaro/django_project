# myfinances/mixins.py

from .models import Statements
from .utils import apply_account_filter


class AccountSelectionMixin:
    """
    Provides:
    - get_acct_infos(): list of accounts for the user's group
    - apply_account_filter(): filters a queryset by ?acct=XXXX
    """

    def get_acct_infos(self, request):
        return (
            Statements.objects
            .filter(user_group__in=request.user.groups.all())
            .values_list("Acct_Info", flat=True)
            .distinct()
            .order_by("Acct_Info")
        )

    def apply_account_filter(self, request, qs):
        return apply_account_filter(request, qs)
