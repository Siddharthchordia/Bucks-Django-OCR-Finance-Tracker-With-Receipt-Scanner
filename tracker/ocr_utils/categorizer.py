import sys
import os
import difflib

# Add parent directory to path to import category_keywords

try:
    from .category_keywords import CATEGORY_KEYWORDS
except ImportError:
    # Fallback if import fails
    print("Warning: Could not import CATEGORY_KEYWORDS. Using empty dict.")
    CATEGORY_KEYWORDS = {}

class ReceiptCategorizer:
    def __init__(self):
        self.categories = CATEGORY_KEYWORDS

    def categorize(self, text):
        """
        Categorizes the receipt text based on keywords using fuzzy matching.
        :param text: Text extracted from the receipt.
        :return: The best matching category or 'Unknown'.
        """
        if not text:
            return "Unknown"

        text = text.lower()
        best_category = "Unknown"
        max_score = 0 # Score based on match length and quality

        # Flatten keywords for easier matching if needed, but iterating is fine
        for category, keywords in self.categories.items():
            # 1. Exact substring match
            for keyword in keywords:
                if keyword in text:
                    # Score = length of keyword. Longer matches are more significant.
                    # e.g. "starbucks" (9) > "ta" (2)
                    score = len(keyword)
                    # Boost score for exact word matches if possible, but for now length is a good proxy
                    
                    if score > max_score:
                        max_score = score
                        best_category = category
            
            # 2. Fuzzy match (only if no strong exact match found yet? or always?)
            # Let's keep fuzzy match as a fallback or secondary check.
            # If we already have a good match (len > 3), maybe skip fuzzy?
            # But fuzzy might find a long word that is slightly misspelled.
            
            tokens = text.split()
            for keyword in keywords:
                # Skip short keywords for fuzzy matching to avoid noise
                if len(keyword) < 4:
                    continue
                    
                matches = difflib.get_close_matches(keyword, tokens, n=1, cutoff=0.8)
                if matches:
                    # If we found a fuzzy match, how do we score it?
                    # Maybe length of keyword * 0.9 (penalty for not being exact)
                    score = len(keyword) * 0.9
                    if score > max_score:
                        max_score = score
                        best_category = category

        return best_category
