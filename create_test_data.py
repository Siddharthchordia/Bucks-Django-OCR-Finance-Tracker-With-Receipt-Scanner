import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_project.settings')
django.setup()

from tracker.models import User, Transaction, Category
from tracker.factories import TransactionFactory, UserFactory, CategoryFactory

def create_data():
    username = "testuser"
    password = "test"
    
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"User {username} already exists.")
    else:
        user = User.objects.create_user(username=username, password=password)
        print(f"Created user {username} with password {password}")

    # Ensure categories exist
    categories = ["Food", "Transport", "Entertainment", "Utilities", "Salary"]
    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)

    print("Creating transactions...")
    
    # Create income and expenses for the last 7 days
    today = date.today()
    for i in range(7):
        d = today - timedelta(days=i)
        
        # Income (Salary)
        if i == 0: # Salary on one day
            cat = Category.objects.get(name="Salary")
            TransactionFactory(user=user, date=d, type='income', amount=5000, category=cat)
        
        # Expenses
        cat = Category.objects.get(name=random.choice(categories[:-1])) # Exclude Salary
        TransactionFactory(user=user, date=d, type='expense', amount=random.randint(20, 100), category=cat)
        
    print("Transactions created.")

if __name__ == "__main__":
    create_data()
