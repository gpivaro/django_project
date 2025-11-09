import pandas as pd
import re
import logging
logger = logging.getLogger(__name__)



class TransactionLabeler:
    """
    A class to clean, filter, and categorize financial transactions using regular expression matching.

    Attributes:
        raw_df (pd.DataFrame): Original transaction data.
        categories_df (pd.DataFrame): DataFrame containing regex expressions and category groups.
        start_date (str): Start date for filtering transactions.
        end_date (str): End date for filtering transactions.
        folder (str): Optional folder path for exporting results.
        patterns (list): List of regex expressions used for matching.
        categories_list (list): Unique list of category groups.
        cleaned_df (pd.DataFrame): Cleaned version of the transaction data.
        filtered_df (pd.DataFrame): Date-filtered and categorized transaction data.
    """

    def __init__(self, transactions_df, categories_df, start_date, end_date, folder=''):
        """
        Initialize the TransactionLabeler with transaction and category data.

        Args:
            transactions_df (pd.DataFrame or list): Raw transaction data.
            categories_df (pd.DataFrame): Category expressions and groups.
            start_date (str): Start date for filtering.
            end_date (str): End date for filtering.
            folder (str): Optional folder path for CSV export.
        """
        self.raw_df = pd.DataFrame(transactions_df)
        self.categories_df = categories_df.sort_values("Expression")
        self.start_date = start_date
        self.end_date = end_date
        self.patterns = list(self.categories_df["Expression"])
        self.groups = list(self.categories_df["Group"])
        self.categories_list = sorted(set(self.groups))
        self.cleaned_df = None
        self.filtered_df = None
        self.folder = folder

    def clean_data(self):
        """
        Clean and normalize the raw transaction data:
        - Convert dates
        - Drop unused columns
        - Ensure numeric types
        - Fill missing values
        """
        df = self.raw_df.copy()
        df["Date"] = pd.to_datetime(df["Posting Date"], errors="coerce")
        df.drop(columns=["Posting Date"], inplace=True)
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Balance"] = pd.to_numeric(df["Balance"].replace(" ", 0), errors="coerce")
        df["Check"] = df["Check"].fillna(0)
        self.cleaned_df = df

    def filter_by_date(self):
        """
        Filter cleaned transactions between start_date and end_date.
        If dates are not provided, use the full available range.
        """
        if self.cleaned_df is None:
            self.clean_data()

        df = self.cleaned_df.copy()
        start = pd.to_datetime(self.start_date or df["Date"].min())
        end = pd.to_datetime(self.end_date or df["Date"].max())

        filtered = df[(df["Date"] >= start) & (df["Date"] <= end)].sort_values("Date", ascending=False)
        filtered.reset_index(drop=True, inplace=True)
        self.filtered_df = filtered

    def categorize_transactions_regex(self):
        """
        Categorize transactions using regular expression matching.
        Assigns the first matching category found in the pattern list.
        """
        if self.filtered_df is None:
            raise ValueError("Filtered transactions not available. Run filter_by_date first.")

        descriptions = self.filtered_df["Description"].fillna("")
        category_matches = []

        for desc in descriptions:
            matched_category = ""
            for pattern, group in zip(self.patterns, self.groups):
                if re.search(pattern, desc):
                    matched_category = group
                    break
            category_matches.append(matched_category)

        self.filtered_df["Category"] = pd.Series(category_matches, dtype="category")

    def export_to_csv(self):
        """
        Export the filtered and categorized transactions to a CSV file.
        Filename includes the date range.
        """
        if self.filtered_df is None:
            raise ValueError("No categorized data to export.")
        if self.folder:
            filename = f"{self.folder}/month_transactions_from_{self.start_date}_to_{self.end_date}.csv"
            self.filtered_df.to_csv(filename, index=False)

    def get_results(self):
        """
        Return the categorized transactions and the list of categories.

        Returns:
            dict: Contains 'statement_dict' and 'categories_list'.
        """
        if self.filtered_df is None:
            raise ValueError("No categorized data available.")

        logger.info(f"Transactions Categorized: {(self.filtered_df['Category']!='').sum()} of {len(self.filtered_df)}.")

        return {
            "statement_dict": self.filtered_df.to_dict("records"),
            "categories_list": self.categories_list
        }


def label_transactions(transactions_df, categories_df, start_date="", end_date="", folder=None):
    """
    Process and categorize transactions using regex matching.

    Args:
        transactions_df (pd.DataFrame or list): Raw transaction data.
        categories_df (pd.DataFrame): Category expressions and groups.
        start_date (str): Start date for filtering.
        end_date (str): End date for filtering.
        folder (str): Optional folder path for CSV export.

    Returns:
        dict: Contains categorized transactions and category list.
    """
    labeler = TransactionLabeler(transactions_df, categories_df, start_date, end_date, folder=folder)
    labeler.clean_data()
    labeler.filter_by_date()
    labeler.categorize_transactions_regex()
    labeler.export_to_csv()
    return labeler.get_results()