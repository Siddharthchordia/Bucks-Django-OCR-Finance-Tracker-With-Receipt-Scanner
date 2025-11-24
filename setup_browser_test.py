import os
import django
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finance_project.settings")
django.setup()

from tracker.models import User, Category

# Create test user
username = 'browser_test_user'
password = 'password'
email = 'test@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, password=password, email=email)
    print(f"User {username} created.")
else:
    print(f"User {username} already exists.")

# Create dummy receipt image
img = Image.new('RGB', (400, 600), color='white')
d = ImageDraw.Draw(img)

# Try to load a default font, otherwise use default
try:
    # This path is common on macOS
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
except IOError:
    font = ImageFont.load_default()

d.text((10, 10), "Store Name", fill=(0, 0, 0), font=font)
d.text((10, 50), "Date: 2023-10-27", fill=(0, 0, 0), font=font)
d.text((10, 100), "Item 1   50.00", fill=(0, 0, 0), font=font)
d.text((10, 130), "Item 2  100.00", fill=(0, 0, 0), font=font)
d.text((10, 200), "Total   150.00", fill=(0, 0, 0), font=font)
d.text((10, 250), "Payment: Credit Card", fill=(0, 0, 0), font=font)

img.save('test_receipt.png')
print("test_receipt.png created.")
