# 💰 Bucks - Personal Finance Tracker

A modern Django-based personal finance tracker with intelligent bill scanning and OCR capabilities. Track your income, expenses, and visualize your financial data with interactive charts.

## ✨ Features

- **📊 Dashboard & Analytics**
  - Interactive charts for weekly, monthly, and category-wise expense tracking
  - Income vs. Expense visualization
  - Real-time financial insights

- **🧾 Smart Bill Scanning**
  - OCR-powered receipt scanning using Tesseract
  - Automatic extraction of date, amount, and transaction type
  - Intelligent category classification based on receipt content
  - Receipt preview during transaction creation

- **💳 Transaction Management**
  - Add, edit, and delete transactions
  - Filter and search transactions
  - Import/Export transactions (CSV/Excel)
  - Pagination for large datasets

- **📈 Interactive Charts**
  - Weekly income/expense trends
  - Monthly budget overview
  - Category-wise expense breakdown
  - Responsive chart legends

- **🌓 Modern UI**
  - Dark theme optimized for readability
  - HTMX for dynamic interactions
  - Responsive design

## 🚀 Technology Stack

- **Backend**: Django 4.x
- **Frontend**: HTML, TailwindCSS, DaisyUI
- **Database**: SQLite (development) - easily configurable for PostgreSQL
- **OCR**: Tesseract OCR, Pillow
- **Charts**: Chart.js
- **Dynamic Updates**: django-htmx
- **Authentication**: django-allauth

## 📋 Prerequisites

- Python 3.8+
- Tesseract OCR
- pip

### Installing Tesseract OCR

**macOS**:
```bash
brew install tesseract
```

**Ubuntu/Debian**:
```bash
sudo apt-get install tesseract-ocr
```

**Windows**:
Download installer from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/Siddharthchordia/Bucks.git
cd Bucks
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create a superuser**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
Open your browser and navigate to `http://localhost:8000`

## 📱 Usage

### Adding Transactions

1. **Manual Entry**: Click "Add Transaction" and fill in the form
2. **Bill Scanning**: Upload a receipt image to auto-fill transaction details
   - The OCR will extract the date, amount, and categorize the transaction
   - Preview the scanned receipt before saving
   - Edit any auto-filled values as needed

### Viewing Analytics

- Navigate to the "Charts" section
- Use navigation controls to view previous/next weeks or months
- View category-wise expense breakdown
- Track monthly income vs. expenses

### Import/Export

- **Export**: Filter your transactions and export to Excel
- **Import**: Upload CSV files with transaction data

## 🎨 OCR Features

The bill scanning feature uses advanced pattern matching to extract:

- **Dates**: Supports 20+ date formats including ISO, DD/MM/YYYY, Month Day Year, etc.
- **Amounts**: Identifies total amounts using keyword detection
- **Categories**: Automatically categorizes based on merchant/item keywords
- **Transaction Type**: Distinguishes between income and expense transactions

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Production Settings

For production deployment:
- Set `DEBUG=False`
- Use a production database (PostgreSQL recommended)
- Configure `ALLOWED_HOSTS` properly
- Set up static files serving
- Use environment variables for sensitive data

## 📂 Project Structure

```
Bucks/
├── finance_project/      # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── templates/
├── tracker/              # Main app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── ocr_utils/       # OCR processing modules
│   │   ├── extractor.py
│   │   ├── categorizer.py
│   │   └── transaction_classifier.py
│   └── templates/
├── static/              # Static files (CSS, JS, images)
├── requirements.txt
└── manage.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Tesseract OCR for text extraction
- Chart.js for beautiful charts
- Django community for the excellent framework
- HTMX for seamless dynamic interactions

## 📧 Contact

Siddharth Chordia - [@siddharthhchordia](https://instagram.com/siddharthhchordia)

Project Link: [https://github.com/yourusername/Bucks](https://github.com/yourusername/Bucks)
