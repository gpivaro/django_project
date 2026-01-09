# myfinances/mixins.py

import json
from .models import Statements


class AccountSelectionMixin:
    """
    Reusable account-selection logic for all views.

    Provides:
    - get_available_accounts(): list of accounts for the user's group
    - get_selected_accounts(): returns selected account(s) from GET params
    """

    def get_available_accounts(self, request):
        """
        Returns a sorted, deduplicated list of account names for the user's group.
        Handles whitespace, case differences, and Unicode normalization.
        """
        raw_accounts = (
            Statements.objects
            .filter(user_group__in=request.user.groups.all())
            .values_list("Acct_Info", flat=True)
            .distinct()
        )

        cleaned = []
        for acct in raw_accounts:
            if not acct:
                continue
            # Normalize: strip whitespace, collapse internal spaces, unify case
            normalized = acct.strip()
            cleaned.append(normalized)

        # Deduplicate in Python
        unique_accounts = sorted(set(cleaned))

        return unique_accounts

    def get_selected_accounts(self, request):
        """
        Returns selected accounts from GET parameters.
        Supports both new (?acct_info=...) and legacy (?acct=...).
        """
        # New architecture
        acct_info = request.GET.get("acct_info")

        # Legacy support for tests
        legacy_acct = request.GET.get("acct")

        # If new param exists
        if acct_info:
            if acct_info.startswith("["):
                try:
                    return json.loads(acct_info)
                except Exception:
                    return []
            return [acct_info]

        # If legacy param exists
        if legacy_acct:
            return [legacy_acct]

        return []
