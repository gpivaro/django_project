import pandas as pd
import re
from thefuzz import process


class TransactionLabeler:
    """
    A class to clean, filter, and categorize financial transactions using regex or fuzzy matching.

    Attributes:
        raw_df (pd.DataFrame): Original transaction data.
        categories_df (pd.DataFrame): DataFrame containing expressions and category groups.
        start_date (str): Start date for filtering transactions.
        end_date (str): End date for filtering transactions.
        folder (str): Optional folder path for exporting results.
        patterns (list): List of expressions used for matching.
        categories_list (list): Unique list of category groups.
        cleaned_df (pd.DataFrame): Cleaned version of the transaction data.
        filtered_df (pd.DataFrame): Date-filtered and categorized transaction data.
    """

    def __init__(self, transactions_df, categories_df, start_date, end_date, folder=''):
        """
        Initialize the TransactionLabeler with transaction and category data.

        Args:
            transactions_df (pd.DataFrame): Raw transaction data.
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
        self.categories_list = sorted(self.categories_df["Group"].unique())
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
        df["Date"] = pd.to_datetime(df["Posting Date"])
        df.drop(columns=["Posting Date"], inplace=True)
        df["Amount"] = df["Amount"].astype(float)
        df.loc[df["Balance"] == " ", "Balance"] = 0
        df["Balance"] = df["Balance"].astype(float)
        df["Check"] = df["Check"].fillna(0)  # Avoid chained assignment warning
        self.cleaned_df = df

    def filter_by_date(self):
        """
        Filter cleaned transactions between start_date and end_date.
        If dates are not provided, use the full available range.
        """
        if self.cleaned_df is None:
            self.clean_data()

        df = self.cleaned_df.copy()
        oldest_date = df["Date"].min()
        newest_date = df["Date"].max()

        start_date = pd.to_datetime(self.start_date or oldest_date)
        end_date = pd.to_datetime(self.end_date or newest_date)

        filtered = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].sort_values("Date", ascending=False)
        filtered.reset_index(drop=True, inplace=True)
        self.filtered_df = filtered

    def categorize_transactions_fuzzy(self):
        """
        Categorize transactions using fuzzy string matching.
        Matches each transaction description to the closest expression.
        """
        if self.filtered_df is None:
            raise ValueError("Filtered transactions not available. Run filter_by_date first.")

        matched_list = []
        for _, row in self.filtered_df.iterrows():
            description = row["Description"]
            best_match = process.extractOne(description, self.patterns)
            expression_index = self.patterns.index(best_match[0])
            matched_group = self.categories_df["Group"].iloc[expression_index]
            matched_expression = self.categories_df["Expression"].iloc[expression_index]
            matched_list.append({
                "matched_expressions": matched_expression,
                "Category": matched_group
            })

        matched_df = pd.DataFrame(matched_list)
        self.filtered_df = pd.concat([self.filtered_df, matched_df], axis=1)

    def categorize_transactions_reg_expression(self):
        """
        Categorize transactions using regular expression matching.
        Assigns the first matching category found in the pattern list.
        """
        category_matches = []

        for _, row in self.filtered_df.iterrows():
            text = row["Description"]
            matched_category = ""

            for pattern, group in zip(self.patterns, self.categories_df["Group"]):
                if re.search(pattern, text):
                    matched_category = group
                    break

            category_matches.append(matched_category)

        self.filtered_df["Category"] = category_matches

    def export_to_csv(self):
        """
        Export the filtered and categorized transactions to a CSV file.
        Filename includes the date range.
        """
        if self.filtered_df is None:
            raise ValueError("No categorized data to export.")
        if self.folder is not None:
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
        
        print(f"Transactions Categorized: {(self.filtered_df['Category']!='').sum()} of {len(self.filtered_df)}.")
        return {
            "statement_dict": self.filtered_df.to_dict("records"),
            "categories_list": self.categories_list
        }
        


def label_transactions(transactions_df, categories_df, start_date="", end_date="",folder=None):
    """ Received the transactions data, the list of categorized transactions, the start and end date.
    Adjust the list of transactions of the data, clean the data and categorize it. 
    Return the transactions categorized and the categories list.
    """
    
    # categories_df = pd.read_csv('./ignore_folder/categories.csv')
    # transactions_df = pd.read_csv('./ignore_folder/chase_statement.csv')
    labeler = TransactionLabeler(transactions_df, categories_df,start_date,end_date,folder=folder)
    labeler.clean_data()
    labeler.filter_by_date()
    labeler.categorize_transactions_reg_expression()
    labeler.export_to_csv()
    results = labeler.get_results()
    
    return {"statement_dict": results["statement_dict"], "categories_list": results["categories_list"]}