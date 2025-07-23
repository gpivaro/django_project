import pandas as pd
from thefuzz import process


start_date = ""
end_date = ""


# Read Categories in Data Base
categories_words_cleaned_df = pd.read_csv('C:\\Users\\gfp1\\Desktop\\GabrielCoding\\categories.csv')
categories_words_cleaned_df.head()


# Convert the input data in a dataframe
chase_df = pd.read_csv("C:\\Users\\gfp1\\Desktop\\Chase\\Chase_Statements\\Chase0497_Activity_20220701.CSV",index_col=False)

chase_df["Date"] = chase_df["Posting Date"].astype("datetime64[ns]")
chase_df.drop(columns=["Posting Date"], inplace=True)
chase_df["Amount"] = chase_df["Amount"].astype("float")

# Create new dataframe
chase_new_df = chase_df.copy(deep=True)

# Fill the empty values for the pending transactions balance
chase_new_df["Balance"].iloc[0] == " "
chase_new_df["Balance"].loc[chase_new_df["Balance"] == " "] = 0
chase_new_df["Balance"] = chase_new_df["Balance"].astype("float")

# Set NAN values to 0
chase_new_df["Check"].loc[chase_new_df["Check"].isnull() == True] = 0

# Get the oldest and the newest date
oldest_date = chase_new_df["Date"].min()
newest_date = chase_new_df["Date"].max()

# Verify if a start date was provided. If not use the oldest date
if start_date == "":
    start_date = oldest_date

# Verify if a end date was provided. If not use the newest date
if end_date == "":
    end_date = newest_date

# Filtering dataset entries
month_transactions = chase_new_df.loc[
    (chase_new_df["Date"] >= start_date) & (chase_new_df["Date"] <= end_date)
].sort_values("Date", ascending=False)

# Reset the ndex to index the transactions on the new order
month_transactions.reset_index(inplace=True)

# Drop columns for visualization purposes
month_transactions.drop(columns=["index"], inplace=True)

# Convert Expressions to list
patterns = categories_words_cleaned_df['Expression'].to_list()

matched_list = []

# Get sentence to match (transaction)
for _,row in month_transactions.iterrows():
    transactions = row['Description']

    # Best match
    best_match = process.extractOne(transactions, patterns)

    # Index of best match
    expression_index = patterns.index(best_match[0]) 
    matched_group = categories_words_cleaned_df['Group'].iloc[expression_index]
    matched_expressions = categories_words_cleaned_df['Expression'].iloc[expression_index]
    matched_list.append({'matched_expressions':matched_expressions,'matched_group':matched_group})
    # print(f"Description: {transactions} : Found Best Match: {matched_group}:{matched_expressions}")

    

# Merge transactions with best match categories
month_transactions = month_transactions.merge(pd.DataFrame(matched_list),left_index=True, right_index=True)
month_transactions.rename(columns = {'matched_group':'Category'},inplace=True)

# Save transactions and best match
month_transactions.to_csv('C:\\Users\\gfp1\\Desktop\\GabrielCoding\\categorized_transactions.csv',index=False)

month_transactions.sample(10)




