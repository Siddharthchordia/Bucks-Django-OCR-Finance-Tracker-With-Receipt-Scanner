from django.urls import path
from tracker import views


urlpatterns = [
    path("", views.index, name='index'),
    path("transactions/", views.transactions_list,name = "transactions-list"),
    path('transactions/create/',views.create_transaction, name = 'create-transaction'),
    path('transactions/<int:pk>/update/',views.update_transaction,name='update-transaction'),
    path('transactions/<int:pk>/delete/',views.delete_transaction,name='delete-transaction'),
    path('get-transactions/',views.get_transaction, name = 'get-transactions'),

    path('transactions/export', views.export, name='export'),
    path('transactions/import', views.import_transaction, name='import'),
    path('transactions/scan/', views.scan_receipt, name='scan-receipt'),

    path("charts/", views.charts_page, name="charts-page"),
    path("api/charts/weekly/", views.api_chart_weekly, name="api-chart-weekly"),
    path("api/charts/categories/", views.api_chart_categories, name="api-chart-categories"),
    path("api/charts/monthly/", views.api_chart_monthly, name="api-chart-monthly"),
]
