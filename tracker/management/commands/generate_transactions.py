import random
from datetime import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from tracker.models import User, Transaction, Category
from tracker.factories import TransactionFactory, CategoryFactory

class Command(BaseCommand):
    help = "Generates transactions for testing"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of transactions to generate (default: 100)'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username to generate transactions for (default: testuser)'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            default=None,
            help='Start date for transactions (format: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            default=None,
            help='End date for transactions (format: YYYY-MM-DD, default: today)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        username = options['username']
        start_date_str = options['start_date']
        end_date_str = options['end_date']
        
        # Parse dates
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime(year=2022, month=1, day=1).date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()
        
        # Create Categories
        categories = ["Bill", "Food", "Clothes", "Medical", "Housing", "Salary", "Social", "Education", "Transport", "Travel"]
        for category in categories:
            Category.objects.get_or_create(name=category)
        
        # Get or create user
        user = User.objects.filter(username=username).first()
        
        if not user:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found. Creating user...'))
            user = User.objects.create_superuser(username=username, password="test")
            self.stdout.write(self.style.SUCCESS(f'Created user "{username}"'))
        
        # Generate transactions using TransactionFactory
        self.stdout.write(f'Generating {count} transactions for user "{username}" between {start_date} and {end_date}...')
        
        fake = Faker()
        categories_list = Category.objects.all()
        types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]
        
        for i in range(count):
            # Generate random date within range
            random_date = fake.date_between(start_date=start_date, end_date=end_date)
            
            # Create transaction with custom date
            Transaction.objects.create(
                user=user,
                category=random.choice(categories_list),
                amount=random.uniform(20, 5000),
                date=random_date,
                type=random.choice(types)
            )
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Generated {i + 1}/{count} transactions...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} transactions for user "{username}"'))
