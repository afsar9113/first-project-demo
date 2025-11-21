# personal_finance_manager.py

import datetime
import os

class Transaction:
    def __init__(self, amount, category, transaction_type, date, description=""):
        self.amount = amount
        self.category = category
        self.type = transaction_type  # 'income' or 'expense'
        self.date = date
        self.description = description
    
    def to_dict(self):
        return {
            'amount': self.amount,
            'category': self.category,
            'type': self.type,
            'date': self.date.strftime("%Y-%m-%d"),
            'description': self.description
        }

class FinanceManager:
    def __init__(self, data_file="finance_data.txt"):
        self.data_file = data_file
        self.transactions = []
        self.budgets = {}
        self.categories = {
            'income': ['Salary', 'Freelance', 'Investment', 'Gift', 'Other'],
            'expense': ['Food', 'Transport', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Education', 'Other']
        }
        self.load_data()
    
    def save_data(self):
        """Save transactions and budgets to file"""
        try:
            with open(self.data_file, 'w') as f:
                # Save transactions
                f.write("[TRANSACTIONS]\n")
                for transaction in self.transactions:
                    f.write(f"{transaction.amount},{transaction.category},{transaction.type},{transaction.date.strftime('%Y-%m-%d')},{transaction.description}\n")
                
                # Save budgets
                f.write("[BUDGETS]\n")
                for category, amount in self.budgets.items():
                    f.write(f"{category},{amount}\n")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load transactions and budgets from file"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r') as f:
                lines = f.readlines()
                section = None
                
                for line in lines:
                    line = line.strip()
                    if line == "[TRANSACTIONS]":
                        section = "transactions"
                        continue
                    elif line == "[BUDGETS]":
                        section = "budgets"
                        continue
                    elif not line:
                        continue
                    
                    if section == "transactions":
                        parts = line.split(',')
                        if len(parts) >= 4:
                            try:
                                amount = float(parts[0])
                                category = parts[1]
                                transaction_type = parts[2]
                                date = datetime.datetime.strptime(parts[3], "%Y-%m-%d").date()
                                description = parts[4] if len(parts) > 4 else ""
                                
                                transaction = Transaction(amount, category, transaction_type, date, description)
                                self.transactions.append(transaction)
                            except ValueError:
                                continue
                    
                    elif section == "budgets":
                        parts = line.split(',')
                        if len(parts) == 2:
                            try:
                                category = parts[0]
                                amount = float(parts[1])
                                self.budgets[category] = amount
                            except ValueError:
                                continue
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def add_transaction(self, amount, category, transaction_type, description=""):
        """Add a new transaction"""
        if transaction_type not in ['income', 'expense']:
            return False, "Invalid transaction type"
        
        if category not in self.categories[transaction_type]:
            return False, "Invalid category"
        
        try:
            amount = float(amount)
            if amount <= 0:
                return False, "Amount must be positive"
            
            transaction = Transaction(amount, category, transaction_type, datetime.date.today(), description)
            self.transactions.append(transaction)
            self.save_data()
            return True, "Transaction added successfully"
        except ValueError:
            return False, "Invalid amount"
    
    def set_budget(self, category, amount):
        """Set monthly budget for a category"""
        if category not in self.categories['expense']:
            return False, "Invalid expense category"
        
        try:
            amount = float(amount)
            if amount < 0:
                return False, "Budget cannot be negative"
            
            self.budgets[category] = amount
            self.save_data()
            return True, f"Budget for {category} set to ${amount:.2f}"
        except ValueError:
            return False, "Invalid amount"
    
    def get_balance(self):
        """Calculate current balance"""
        income = sum(t.amount for t in self.transactions if t.type == 'income')
        expenses = sum(t.amount for t in self.transactions if t.type == 'expense')
        return income - expenses
    
    def get_monthly_summary(self, year=None, month=None):
        """Get monthly summary of income and expenses"""
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
        
        monthly_income = 0
        monthly_expenses = 0
        category_expenses = {}
        
        for transaction in self.transactions:
            if transaction.date.year == year and transaction.date.month == month:
                if transaction.type == 'income':
                    monthly_income += transaction.amount
                else:
                    monthly_expenses += transaction.amount
                    category_expenses[transaction.category] = category_expenses.get(transaction.category, 0) + transaction.amount
        
        return {
            'income': monthly_income,
            'expenses': monthly_expenses,
            'savings': monthly_income - monthly_expenses,
            'category_expenses': category_expenses
        }
    
    def get_spending_analysis(self):
        """Analyze spending patterns and provide insights"""
        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        
        # Current month data
        current_data = self.get_monthly_summary(current_year, current_month)
        
        # Previous month data
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        prev_data = self.get_monthly_summary(prev_year, prev_month)
        
        insights = []
        
        # Savings comparison
        current_savings = current_data['savings']
        prev_savings = prev_data['savings']
        
        if current_savings > prev_savings:
            insights.append(f"Great! Your savings increased by ${(current_savings - prev_savings):.2f} compared to last month")
        elif current_savings < prev_savings:
            insights.append(f"Warning: Your savings decreased by ${(prev_savings - current_savings):.2f} compared to last month")
        
        # Budget analysis
        for category, spent in current_data['category_expenses'].items():
            budget = self.budgets.get(category, 0)
            if budget > 0:
                percentage = (spent / budget) * 100
                if percentage > 100:
                    insights.append(f"You exceeded your {category} budget by {percentage - 100:.1f}%")
                elif percentage > 80:
                    insights.append(f"Warning: You've used {percentage:.1f}% of your {category} budget")
        
        # Top spending category
        if current_data['category_expenses']:
            top_category = max(current_data['category_expenses'].items(), key=lambda x: x[1])
            insights.append(f"Your highest spending category is {top_category[0]} (${top_category[1]:.2f})")
        
        return insights
    
    def generate_report(self, year=None, month=None):
        """Generate a detailed financial report"""
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
        
        summary = self.get_monthly_summary(year, month)
        
        report = []
        report.append(f"Financial Report for {month}/{year}")
        report.append("=" * 40)
        report.append(f"Income: ${summary['income']:.2f}")
        report.append(f"Expenses: ${summary['expenses']:.2f}")
        report.append(f"Savings: ${summary['savings']:.2f}")
        report.append(f"Saving Rate: {(summary['savings']/summary['income']*100 if summary['income'] > 0 else 0):.1f}%")
        report.append("")
        report.append("Expense Breakdown:")
        
        for category, amount in summary['category_expenses'].items():
            budget = self.budgets.get(category, 0)
            budget_status = f" (Budget: ${budget:.2f})" if budget > 0 else ""
            report.append(f"  {category}: ${amount:.2f}{budget_status}")
        
        return "\n".join(report)

class UserInterface:
    def __init__(self):
        self.finance_manager = FinanceManager()
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("       PERSONAL FINANCE MANAGER")
        print("="*50)
        print("1. Add Income")
        print("2. Add Expense")
        print("3. Set Budget")
        print("4. View Balance")
        print("5. Monthly Summary")
        print("6. Spending Analysis")
        print("7. Generate Report")
        print("8. View All Transactions")
        print("9. Exit")
        print("="*50)
    
    def add_income(self):
        """Handle adding income transaction"""
        print("\n--- Add Income ---")
        print("Categories:", ", ".join(self.finance_manager.categories['income']))
        
        category = input("Enter category: ").strip()
        if category not in self.finance_manager.categories['income']:
            print("Invalid category!")
            return
        
        amount = input("Enter amount: ").strip()
        description = input("Enter description (optional): ").strip()
        
        success, message = self.finance_manager.add_transaction(amount, category, 'income', description)
        print(message)
    
    def add_expense(self):
        """Handle adding expense transaction"""
        print("\n--- Add Expense ---")
        print("Categories:", ", ".join(self.finance_manager.categories['expense']))
        
        category = input("Enter category: ").strip()
        if category not in self.finance_manager.categories['expense']:
            print("Invalid category!")
            return
        
        amount = input("Enter amount: ").strip()
        description = input("Enter description (optional): ").strip()
        
        success, message = self.finance_manager.add_transaction(amount, category, 'expense', description)
        print(message)
    
    def set_budget(self):
        """Handle setting budget"""
        print("\n--- Set Budget ---")
        print("Categories:", ", ".join(self.finance_manager.categories['expense']))
        
        category = input("Enter category: ").strip()
        if category not in self.finance_manager.categories['expense']:
            print("Invalid category!")
            return
        
        amount = input("Enter budget amount: ").strip()
        
        success, message = self.finance_manager.set_budget(category, amount)
        print(message)
    
    def view_balance(self):
        """Display current balance"""
        balance = self.finance_manager.get_balance()
        print(f"\nCurrent Balance: ${balance:.2f}")
        
        if balance > 0:
            print("Status: Positive balance ✓")
        else:
            print("Status: Negative balance ⚠")
    
    def monthly_summary(self):
        """Display monthly summary"""
        try:
            year = int(input("Enter year (leave blank for current): ") or datetime.date.today().year)
            month = int(input("Enter month (1-12, leave blank for current): ") or datetime.date.today().month)
        except ValueError:
            print("Invalid input!")
            return
        
        summary = self.finance_manager.get_monthly_summary(year, month)
        
        print(f"\n--- Monthly Summary ({month}/{year}) ---")
        print(f"Income: ${summary['income']:.2f}")
        print(f"Expenses: ${summary['expenses']:.2f}")
        print(f"Savings: ${summary['savings']:.2f}")
        
        if summary['income'] > 0:
            saving_rate = (summary['savings'] / summary['income']) * 100
            print(f"Saving Rate: {saving_rate:.1f}%")
    
    def spending_analysis(self):
        """Display spending analysis and insights"""
        print("\n--- Spending Analysis ---")
        insights = self.finance_manager.get_spending_analysis()
        
        if insights:
            for insight in insights:
                print(f"• {insight}")
        else:
            print("Not enough data for analysis. Keep tracking your transactions!")
    
    def generate_report(self):
        """Generate and display financial report"""
        try:
            year = int(input("Enter year (leave blank for current): ") or datetime.date.today().year)
            month = int(input("Enter month (1-12, leave blank for current): ") or datetime.date.today().month)
        except ValueError:
            print("Invalid input!")
            return
        
        report = self.finance_manager.generate_report(year, month)
        print(f"\n{report}")
    
    def view_transactions(self):
        """Display all transactions"""
        if not self.finance_manager.transactions:
            print("\nNo transactions found!")
            return
        
        print("\n--- All Transactions ---")
        print("Date       | Type    | Category      | Amount   | Description")
        print("-" * 60)
        
        for transaction in self.finance_manager.transactions:
            print(f"{transaction.date} | {transaction.type:7} | {transaction.category:12} | ${transaction.amount:7.2f} | {transaction.description}")
    
    def run(self):
        """Main application loop"""
        print("Welcome to Personal Finance Manager!")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            try:
                if choice == '1':
                    self.add_income()
                elif choice == '2':
                    self.add_expense()
                elif choice == '3':
                    self.set_budget()
                elif choice == '4':
                    self.view_balance()
                elif choice == '5':
                    self.monthly_summary()
                elif choice == '6':
                    self.spending_analysis()
                elif choice == '7':
                    self.generate_report()
                elif choice == '8':
                    self.view_transactions()
                elif choice == '9':
                    print("Thank you for using Personal Finance Manager!")
                    break
                else:
                    print("Invalid choice! Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    app = UserInterface()
    app.run()