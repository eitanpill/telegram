#!/usr/bin/env python3
import csv
import random
import sys

### START OF ORIGINAL CODE ###
# הקוד המקורי שלך מתחיל כאן.
# לדוגמה, נניח שיש לך פונקציה קיימת למשלוח מוצר:
def send_product(product):
    """
    הפונקציה הקיימת לשליחת המוצר.
    שומרת על הלוגיקה המקורית שלך.
    """
    print("נשלח המוצר:")
    for key, value in product.items():
        print(f"{key}: {value}")

# וכן גם פונקציות או קוד נוסף שנדרש בפעולת הבוט.
### END OF ORIGINAL CODE ###

### NEW FUNCTIONS ADDED (מוסיפים ללא שינוי בקוד הקיים) ###

def get_random_unsent_product(csv_file='ads.csv'):
    """
    בוחרת מוצר רנדומלי מתוך אלה שעדיין לא נשלחו 
    (עבורם העמודה 'sent' אינה שווה ל-'yes').
    """
    unsent_products = []
    try:
        with open(csv_file, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('sent', 'no').strip().lower() != 'yes':
                    unsent_products.append(row)
    except Exception as e:
        print(f"שגיאה בקריאת הקובץ {csv_file}: {e}")
        sys.exit(1)
    
    if not unsent_products:
        return None
    return random.choice(unsent_products)

def mark_product_as_sent(selected_product, csv_file='ads.csv'):
    """
    מסמן את המוצר שנבחר כ"נשלח" על ידי עדכון עמודת 'sent' ל-'yes'.
    נניח שעמודת 'name' היא המזהה הייחודי לכל מוצר.
    """
    updated_rows = []
    try:
        with open(csv_file, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row.get('name') == selected_product.get('name'):
                    row['sent'] = 'yes'
                updated_rows.append(row)
    except Exception as e:
        print(f"שגיאה בקריאת הקובץ לעדכון {csv_file}: {e}")
        sys.exit(1)
    
    try:
        with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
    except Exception as e:
        print(f"שגיאה בכתיבת הקובץ {csv_file}: {e}")
        sys.exit(1)

### NEW INTEGRATION INTO MAIN FUNCTION ###
def main():
    # שמירת הקוד המקורי – אנו לא משנים דבר בקוד הישן
    # כאן אנו מוסיפים את השינויים הנדרשים:
    
    # בחירת מוצר רנדומלי מתוך אלה שעדיין לא נשלחו
    product = get_random_unsent_product()
    if product is None:
        print("אין מוצרים נוספים לשליחה.")
        sys.exit(0)
    
    # קריאה לפונקציה הקיימת שלך למשלוח המוצר
    send_product(product)
    
    # עדכון הקובץ לסימון שהמוצר נשלח
    mark_product_as_sent(product)
    
    # אם יש קוד נוסף בקוד המקורי שלך ב-main – ניתן לשלב אותו כאן

if __name__ == "__main__":
    main()