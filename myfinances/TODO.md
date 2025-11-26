# My-Finances App – Improvement Roadmap

This document tracks planned enhancements and features for the My-Finances application.  
Each item will be tackled separately and marked complete once implemented.

---

## 🔨 Core Improvements

### Create New Categories Model

- [x] Define a new `CategoriesList` model that only stores the **list of available categories**.
- [x] Ensure `Statements` model uses this new `Categories` model for its foreign key.
- [x] Add admin interface for managing available categories.
- [x] Update forms to pull choices from the new `CategoriesList` model.

1. **CSV Upload**

   - [x] Build a separate **Upload page**.
   - [x] Allow users to upload CSV files.
   - [x] Parse and save transactions directly into the `Statements` model.
   - [x] Add validation and error handling for malformed files.
   - [x] Add account number last-4 field to upload form.

2. **Manage Statements Page**

   - [x] Create **ListView** showing statements with categories.
   - [x] Add **UpdateView** to edit statement categories.
   - [ ] Add a **Delete option** so users can remove statements from the database.
   - [ ] Implement **pagination** to handle large datasets efficiently.
   - [ ] Add **filters by date range**.
   - [ ] Add **search functionality** by description and category.
   - [ ] Improve table usability (sticky headers, column resizing, better alignment).

3. **Data Visualization**

   - [x] Build **Category Totals View** with date range filtering.
   - [x] Add grand total calculation.
   - [x] Highlight positive vs. negative totals in the template.
   - [ ] Create a dedicated **Charts page**.
   - [ ] Display categorized statements in **bar charts, pie charts, and trend lines**.
   - [ ] Provide an overview of spending per category.

4. **Export Functionality**

   - [ ] Provide option to **export categorized statements** (CSV/Excel).
   - [ ] Ensure exported files include categories, amounts, and dates.

5. **Dashboard**
   - [ ] Create a **Dashboard page**.
   - [ ] Show key metrics: number of categorized statements, uncategorized statements, totals per category.
   - [ ] Include quick links to Manage Statements, Upload, and Charts.

---

## 🗂 Model Refactor

### Rename Categories → CategorizedTransactions

- [ ] Rename the current `Categories` model to **CategorizedTransactions**.
- [ ] Migrate existing data to the new model name.
- [ ] Update all references in views, forms, and templates to use `CategorizedTransactions`.

---

## 🔐 Encryption & Security

- [ ] Encrypt sensitive fields (e.g., `Acct_Info`) at rest in the database.
- [ ] Use Django’s `FERNET_KEY` or a custom encryption layer for account numbers.
- [ ] Ensure HTTPS is enforced for all uploads and views.
- [ ] Add per-user data isolation checks to prevent cross-user access.
- [ ] Implement audit logging for uploads and edits.

---

## 🎨 User Experience Enhancements

- [x] Center and style tables for better readability.
- [x] Highlight selected date ranges in reports.
- [ ] Add row-level feedback (green/red highlight) after save/delete actions.
- [ ] Improve success/error message placement and styling.
- [ ] Make tables responsive and mobile-friendly.
- [ ] Add tooltips or help text explaining each feature.

---

## 📌 Future Ideas

- [ ] User preferences (default category filters, default export format).
- [ ] Scheduled CSV imports (e.g. via email or API integration).
- [ ] Multi-user support with role-based permissions.
- [ ] Dark mode toggle for better accessibility.

---

## ✅ Tracking Progress

- Use GitHub Issues or project boards to break down each item.
- Mark items as `[x]` when completed.
- Keep this document updated as new ideas arise.
