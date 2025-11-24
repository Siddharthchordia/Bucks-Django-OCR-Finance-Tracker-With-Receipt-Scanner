from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django_htmx.http import retarget
from django.core.paginator import Paginator
from django.conf import settings
from tracker.models import Transaction, Category
from tracker.ocr_utils import process_receipt_image
import os
from django.core.files.storage import FileSystemStorage
from tracker.filters import TransactionFilter
from tracker.forms import TransactionForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseServerError
from django.db.models import Sum
from django.db import DatabaseError
from django.db.models import DateTimeField
from datetime import date, timedelta
from tracker.resources import TransactionResource
from django.http import HttpResponse
from tablib import Dataset
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        today = date.today()
        start_week = today - timedelta(days=6)

        has_weekly_data = Transaction.objects.filter(user=request.user, date__gte=start_week).exists()
        has_expense_data = Transaction.objects.filter(user=request.user, type='expense').exists()
        has_monthly_data = Transaction.objects.filter(user=request.user, date__year=today.year, date__month=today.month).exists()

        context = {
            "has_weekly_data": has_weekly_data,
            "has_expense_data": has_expense_data,
            "has_monthly_data": has_monthly_data,
        }
        return render(request, 'tracker/index.html', context)
    return render(request, 'tracker/index.html')


@login_required
def transactions_list(request):

    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related("category"),
    )
    paginator=Paginator(transaction_filter.qs,settings.PAGE_SIZE)
    txn_page=paginator.page(1)
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    context={
        'transactions':txn_page,
        "filter":transaction_filter,
        "total_income":total_income,
        "total_expenses":total_expenses,
        "net_savings":total_income-total_expenses,
        "net_savings_abs":abs(total_income-total_expenses)
    }
    if request.htmx:
        return render(request,"tracker/partials/transactions-container.html",context)

    return render(request,"tracker/transactions-list.html",context)

@login_required
def create_transaction(request):
    if request.method=="POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.user = request.user
            txn.save()
            context= {"message":"Transaction was added successfully!"}
            return render(request,'tracker/partials/create-transaction-success.html',context)
        else:
            context = {'form':form}
            response= render(request,'tracker/partials/create-transaction.html',context)
            return retarget(response,"#transaction-block")
    context = {"form":TransactionForm()}
    return render(request,'tracker/partials/create-transaction.html',context)

@login_required
def update_transaction(request,pk):
    transaction = get_object_or_404(Transaction,pk=pk, user = request.user)
    if request.method=="POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context= {"message":"Transaction was updated successfully!"}
            return render(request,'tracker/partials/create-transaction-success.html',context)
        else:
            context={
                "form":TransactionForm(instance=transaction),
                "transaction":transaction
            }
            response= render(request,"tracker/partials/update-transaction.html", context)
            return retarget(response,"#transaction-block")

    context={
        "form":TransactionForm(instance=transaction),
        "transaction":transaction
    }


    return render(request,"tracker/partials/update-transaction.html", context)

@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request,pk):
    transaction = get_object_or_404(Transaction,pk=pk,user=request.user)
    transaction.delete()
    context={
        'message':f"Transaction of {transaction.amount} on {transaction.date} was deleted successfully!"
    }
    return render(request,'tracker/partials/create-transaction-success.html',context)

@login_required
def get_transaction(request):
    page = request.GET.get('page',1)
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related("category"),
    )
    paginator=Paginator(transaction_filter.qs,settings.PAGE_SIZE)
    context={
        "transactions":paginator.page(page)
    }
    return render(request,"tracker/partials/transactions-container.html#txn_list",context)


@login_required
def charts_page(request):
    count=Transaction.objects.filter(user=request.user).count()
    today = date.today()
    start_week = today - timedelta(days=6)

    has_weekly_data = Transaction.objects.filter(user=request.user, date__gte=start_week).exists()
    has_expense_data = Transaction.objects.filter(user=request.user, type='expense').exists()
    has_monthly_data = Transaction.objects.filter(user=request.user, date__year=today.year, date__month=today.month).exists()

    context = {
        "count": count,
        "logo_url": "static/images/bucks.svg",
        "has_weekly_data": has_weekly_data,
        "has_expense_data": has_expense_data,
        "has_monthly_data": has_monthly_data,
    }
    return render(request, "tracker/charts.html", context)



@login_required
def api_chart_weekly(request):
    try:
        date_field = Transaction._meta.get_field('date')
        is_datetime = isinstance(date_field, DateTimeField)
    except Exception as e:
        print("api_chart_weekly: failed to inspect Transaction.date field:", e)
        return HttpResponseServerError("Server misconfiguration: cannot inspect Transaction.date field. See server logs.")

    # Get week offset from query parameter (default 0 = current week)
    week_offset = int(request.GET.get('week_offset', 0))
    
    today = date.today()
    # Calculate the start date based on offset
    start = today - timedelta(days=6) + timedelta(weeks=week_offset)

    labels = []
    income_data = []
    expense_data = []

    try:
        # We will query per-day using the correct lookup for the field type.
        for i in range(7):
            d = start + timedelta(days=i)
            labels.append(d.isoformat())

            if is_datetime:
                # Transaction.date is DateTimeField
                income_tot = (
                    Transaction.objects
                    .filter(user=request.user, type="income", date__date=d)
                    .aggregate(total=Sum("amount"))["total"] or 0.0
                )
                expense_tot = (
                    Transaction.objects
                    .filter(user=request.user, type="expense", date__date=d)
                    .aggregate(total=Sum("amount"))["total"] or 0.0
                )
            else:
                # Transaction.date is DateField (use exact match)
                income_tot = (
                    Transaction.objects
                    .filter(user=request.user, type="income", date=d)
                    .aggregate(total=Sum("amount"))["total"] or 0.0
                )
                expense_tot = (
                    Transaction.objects
                    .filter(user=request.user, type="expense", date=d)
                    .aggregate(total=Sum("amount"))["total"] or 0.0
                )

            income_data.append(float(income_tot))
            expense_data.append(float(expense_tot))

    except DatabaseError as db_err:
        print("api_chart_weekly: database error while aggregating:", db_err)
        return HttpResponseServerError("Database error when computing weekly aggregates. See server logs.")

    return JsonResponse({

        "labels": labels,
        "datasets": [
            {"label": "Income", "data": income_data},
            {"label": "Expense", "data": expense_data}
        ]
    })
@login_required
def api_chart_categories(request):
    cnt = Transaction.objects.filter(user=request.user).count()
    qs = Transaction.objects.filter(user=request.user, type="expense")
    # Sum per category name
    cat_qs = (
        qs.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    labels = [entry["category__name"] for entry in cat_qs]
    data = [float(entry["total"]) for entry in cat_qs]

    return JsonResponse({
        "labels":labels,

        "datasets": [
            {"label": "Expenses by Category", "data": data}
        ]
    })

@login_required
def api_chart_monthly(request):
    from dateutil.relativedelta import relativedelta
    
    # Get month offset from query parameter (default 0 = current month)
    month_offset = int(request.GET.get('month_offset', 0))
    
    today = date.today()
    # Calculate the target month based on offset
    target_date = today + relativedelta(months=month_offset)
    
    # Filter for target month
    qs = Transaction.objects.filter(
        user=request.user, 
        date__year=target_date.year, 
        date__month=target_date.month
    )
    
    total_income = qs.filter(type="income").aggregate(t=Sum("amount"))["t"] or 0
    total_expense = qs.filter(type="expense").aggregate(t=Sum("amount"))["t"] or 0
    
    # Calculate savings (Income - Expense)
    # If expenses > income, savings is 0 (or negative, but for chart we might want 0)
    # The requirement says "rest 70% savings", implying we show the remaining part of income.
    # If expenses > income, we might just show 100% expense or handle it gracefully.
    # For now, let's assume savings = income - expense.
    savings = float(total_income) - float(total_expense)
    if savings < 0:
        savings = 0

    return JsonResponse({
        "labels": ["Expense", "Savings"],
        "datasets": [
            {
                "label": "Monthly Overview",
                "data": [float(total_expense), savings],
            }
        ]
    })

@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect':request.get_full_path()})
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related("category"),
    )
    data = TransactionResource().export(transaction_filter.qs)
    response = HttpResponse(data.xlsx,content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    response['Content-Disposition'] = 'attachment;filename = "transactions.xlsx"'
    return response

@login_required
def import_transaction(request):
    if request.method=="POST":
        file = request.FILES.get('file')
        resource = TransactionResource()
        dataset = Dataset()
        dataset.load(file.read().decode(), format='csv')
        res = resource.import_data(dataset, user = request.user,dry_run=True)
        if not res.has_errors():
            resource.import_data(dataset,user=request.user,dry_run=False)
            context={'message':f"{len(dataset)} Transactions were uploaded Successfully"}
        else:
            context={"message":"Sorry! an error occured, please try again!"}
        return render(request, 'tracker/partials/create-transaction-success.html',context)



    return render(request, 'tracker/partials/import-txn.html')

@login_required
def scan_receipt(request):
    if request.method == "POST" and request.FILES.get('receipt_image'):
        image_file = request.FILES['receipt_image']
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        uploaded_file_url = fs.path(filename)

        try:
            # Read and encode image for preview
            import base64
            with open(uploaded_file_url, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Determine mime type (simple check based on extension)
            ext = os.path.splitext(uploaded_file_url)[1].lower()
            mime_type = "image/jpeg" # default
            if ext == ".png":
                mime_type = "image/png"
            elif ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            
            scanned_image_data = f"data:{mime_type};base64,{b64_string}"

            data = process_receipt_image(uploaded_file_url)
            
            # Clean up the file after processing
            if os.path.exists(uploaded_file_url):
                os.remove(uploaded_file_url)

            if "error" in data:
                 return render(request, 'tracker/partials/create-transaction.html', {
                    "form": TransactionForm(),
                    "error": data["error"],
                    "scanned_image": scanned_image_data
                })

            # Map extracted data to form initial data
            initial_data = {
                "amount": data.get("amount"),
                "date": data.get("date"),
                "type": data.get("transaction_type", "expense"), # Default to expense
            }
            
            # Try to find category
            category_name = data.get("category")
            if category_name:
                category = Category.objects.filter(name__iexact=category_name).first()
                if category:
                    initial_data["category"] = category

            form = TransactionForm(initial=initial_data)
            
            return render(request, 'tracker/partials/create-transaction.html', {
                "form": form,
                "scanned_image": scanned_image_data
            })

        except Exception as e:
             # Clean up on error too
            if os.path.exists(uploaded_file_url):
                os.remove(uploaded_file_url)
            return render(request, 'tracker/partials/create-transaction.html', {
                "form": TransactionForm(),
                "error": f"Error processing receipt: {str(e)}"
            })

    return render(request, 'tracker/partials/create-transaction.html', {"form": TransactionForm()})