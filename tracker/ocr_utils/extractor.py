import re
from datetime import datetime

class DataExtractor:
    def __init__(self):
        self.payment_keywords = {
            "UPI": ["upi", "google pay", "phonepe", "paytm", "bhim", "@okhdfc", "@oksbi", "@ybl"],
            "Credit Card": ["credit card", "visa", "mastercard", "amex", "american express"],
            "Debit Card": ["debit card", "maestro", "rupay"],
            "Cash": ["cash", "cash payment"]
        }

    def extract_payment_mode(self, text):
        """
        Extracts the payment mode (UPI, Credit Card, etc.).
        :param text: Text extracted from the receipt.
        :return: Payment mode string or 'Unknown'.
        """
        if not text:
            return "Unknown"
        
        text = text.lower()
        for mode, keywords in self.payment_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return mode
        return "Unknown"


    def extract_date(self, text):
        """
        Extracts the date from the receipt text.
        :param text: Text extracted from the receipt.
        :return: Date string in YYYY-MM-DD format or None.
        """
        import dateutil.parser

        # Common date formats
        # use re.IGNORECASE when compiling most of these
        date_patterns = [
            # 1) ISO / RFC-like
            r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b",  # 2023-05-20T14:30:00Z or 2023-05-20T14:30:00+05:30
            # 2) ISO date/time without T
            r"\b\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(:\d{2})?\b",  # 2023-05-20 14:30 or 2023-05-20 14:30:00
            # 3) Full numeric, common separators (US or Intl)
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # 05/20/2018, 20-05-2018, 5/2/18
            # 4) Dotted numeric
            r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b",  # 20.05.2018, 5.2.18
            # 5) Compact numeric (YYYYMMDD)
            r"\b\d{4}\d{2}\d{2}\b",  # 20180520
            # 6) Compact numeric (DDMMYYYY) - beware false positives
            r"\b\d{2}\d{2}\d{4}\b",  # 20052018 (use carefully)
            # 7) Year-month compact with separator
            r"\b\d{4}[./-]\d{1,2}\b",  # 2018-05, 2018.5
            # 8) Month name + year (e.g., billing)
            r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
            r"[-\s,\.]*\d{2,4}\b",  # May 2018, May-18, October,2018
            # 9) Year + Month name (rare)
            r"\b\d{4}[-\s,\.]*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b",  # 2018 May
            # 10) Day Month Year with separators (space, comma, dash)
            r"\b\d{1,2}[-\s\.](?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[-\,\s\.]\d{2,4}\b",
            # 20 May 2018, 20-May-18, 20. May, 2018
            # 11) Month Day, Year (with optional comma and ordinal)
            r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
            r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+\d{2,4}\b",  # May 20th, 2018
            # 12) Day with ordinal + Month (optional year)
            r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
            r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:,?\s+\d{2,4})?\b",
            # 1st of May 2018, 21st Dec
            # 13) Short year with apostrophe or leading apostrophe
            r"\b(?:\'\d{2}|\d{2}\'|\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-]\'\d{2})\b",
            # '18, 20-May-'18 (some OCR variants)
            # 14) Hyphenated textual month between numbers (your earlier 20-May-18)
            r"\b\d{1,2}[-](?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[-]\d{2,4}\b",
            # 15) Date ranges: "12-14 Oct 2023" or "Oct 12-14, 2023"
            r"\b\d{1,2}(?:st|nd|rd|th)?[-\s]\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
            r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
            r"(?:,?\s+\d{2,4})?\b",
            r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
            r"Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}[-]\d{1,2},?\s+\d{2,4}\b",
            # 16) "from ... to ..." or "dd/mm/yyyy to dd/mm/yyyy"
            r"\b(?:from|to|until|-)\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # partial helper (use with context)
            # 17) Month name with day-month compact (no year) — useful for receipts
            r"\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b",  # 20 May
            # 18) Quarter / Fiscal - Q1 2018, FY2018, FY 18
            r"\bQ[1-4]\s*\d{2,4}\b",
            r"\bFY\s*\d{2,4}\b",
            # 19) Week numbers: Week 32 2018 or 2018-W32 (ISO week)
            r"\bWeek\s*\d{1,2}\s*\d{2,4}\b",
            r"\b\d{4}-W\d{2}\b",  # 2018-W32
            # 20) Time-only (useful if combined with date)
            r"\b\d{1,2}:\d{2}(:\d{2})?\s*(?:AM|PM|am|pm)?\b",  # 2:30 PM, 14:30
            # 21) Partial year-like tokens (just a year)
            r"\b(?:19|20)\d{2}\b",  # 1999, 2023
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for date_str in matches:
                try:
                    # Use dateutil for robust parsing
                    # dayfirst=True is important for DD/MM/YYYY which is common in many regions
                    dt = dateutil.parser.parse(date_str, dayfirst=True)
                    return dt.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
        
        return None

    def extract_amount(self, text):
        """
        Extracts the total amount from the receipt text.
        :param text: Text extracted from the receipt.
        :return: Amount as float or None.
        """
        # Look for "Total", "Amount", "Net Amount" followed by a number
        # This is a heuristic.
        
        # Pattern to find currency-like numbers (e.g., 1,234.56 or 1234.56)
        # We look for the largest number associated with "Total" keywords
        
        lines = text.split('\n')
        amount_candidates = []
        
        total_keywords = ["total", "net amount", "grand total", "amount payable", "final amount", "net pay"]
        
        for line in lines:
            lower_line = line.lower()
            for keyword in total_keywords:
                if keyword in lower_line:
                    # Try to find a number in this line
                    matches = re.findall(r'[\d,]+\.\d{2}', line)
                    if not matches:
                         matches = re.findall(r'[\d,]+', line) # Fallback to integers if no decimals
                    
                    for match in matches:
                        try:
                            val = float(match.replace(',', ''))
                            amount_candidates.append(val)
                        except ValueError:
                            pass
        
        if amount_candidates:
            # Usually the total is the largest number found near "Total" keywords
            # But sometimes it might be a subtotal. 
            # For simplicity, let's take the largest candidate found on lines with "Total"
            return max(amount_candidates)
            
        # If no "Total" keyword found, maybe just look for the largest number in the bottom half of text?
        # That's risky. Let's stick to keyword association for now.
        
        return None
