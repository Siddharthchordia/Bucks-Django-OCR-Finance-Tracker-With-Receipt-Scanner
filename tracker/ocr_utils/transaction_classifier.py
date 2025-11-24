class TransactionClassifier:
    def __init__(self):
        self.income_keywords = [
            "salary", "credit", "deposit", "refund", "cashback", "bonus", 
            "stipend", "dividend", "interest credited", "reimbursement"
        ]
        # Expense is usually the default, but we can look for expense indicators too
        self.expense_keywords = [
            "debit", "payment", "purchase", "bill", "invoice", "total", 
            "amount due", "paid", "checkout", "buy"
        ]

    def classify(self, text):
        """
        Classifies the transaction type as 'Income' or 'Expense'.
        :param text: Text extracted from the receipt.
        :return: 'Income' or 'Expense'.
        """
        if not text:
            return "Expense" # Default to Expense
        
        text = text.lower()
        
        # Check for Income keywords
        for keyword in self.income_keywords:
            if keyword in text:
                # Context check: "Credit Card" contains "Credit" but is usually an expense (payment method).
                # So we need to be careful.
                if keyword == "credit" and "credit card" in text:
                    continue
                return "income"
        
        # If no income keywords found, assume Expense
        return "expense"
