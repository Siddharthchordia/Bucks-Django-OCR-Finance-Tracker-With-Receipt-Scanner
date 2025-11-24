from .ocr_engine import OCREngine
from .categorizer import ReceiptCategorizer
from .transaction_classifier import TransactionClassifier
from .extractor import DataExtractor
def process_receipt_image(image_path):
    """
    Main utility function to process a receipt image.
    """
    # Initialize components
    ocr = OCREngine()
    categorizer = ReceiptCategorizer()
    classifier = TransactionClassifier()
    extractor = DataExtractor()
    # 1. Extract Text
    try:
        raw_text = ocr.extract_text(image_path)
    except Exception as e:
        return {"error": f"OCR failed: {str(e)}"}
    if not raw_text:
        return {"error": "No text extracted"}
    # 2. Process
    data = {
        "raw_text": raw_text,
        "category": categorizer.categorize(raw_text),
        "transaction_type": classifier.classify(raw_text),
        "payment_mode": extractor.extract_payment_mode(raw_text),
        "date": extractor.extract_date(raw_text),
        "amount": extractor.extract_amount(raw_text),
    }
    return data