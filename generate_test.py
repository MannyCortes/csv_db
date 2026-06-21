import csv
import random
from datetime import datetime, timedelta

def generate_chaos_csv(filename="pressure_test10k.csv", num_rows=10000):
    headers = ["Transaction_ID", "Date", "Customer_Name", "Item_Purchased", "Quantity", "Unit_Price", "Total_Amount", "Status"]
    
    # We will force a duplicate ID to test your batch fallback logic
    duplicate_id = 99999 
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for i in range(1, num_rows + 1):
            # 1. The Happy Path (80% of the data)
            if random.random() > 0.2:
                t_id = i
                date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
                name = random.choice(["Manny", "Starla", "Kennadee", "Samme"])
                item = random.choice(["Pokémon Cards", "Cologne", "Pizza", "Lowering Kit"])
                qty = random.randint(1, 5)
                price = round(random.uniform(10.0, 150.0), 2)
                total = round(qty * price, 2)
                status = random.choice(["Completed", "Pending"])
                writer.writerow([t_id, date, name, item, qty, price, total, status])
            
            # 2. The Chaos Path (20% of the data)
            else:
                error_type = random.choice(["duplicate_id", "bad_date", "string_in_float", "missing_value"])
                
                if error_type == "duplicate_id":
                    # This will trigger your SQLAlchemy IntegrityError
                    writer.writerow([duplicate_id, "2026-06-08", "Duplicate Dan", "Item", 1, 10.0, 10.0, "Completed"])
                
                elif error_type == "bad_date":
                    # Regex should catch this (MM/DD/YYYY instead of YYYY-MM-DD)
                    writer.writerow([i, "06/08/2026", "Format Fred", "Item", 1, 10.0, 10.0, "Completed"])
                    
                elif error_type == "string_in_float":
                    # Regex should catch this
                    writer.writerow([i, "2026-06-08", "Shifted Sam", "Item", 1, "Ten Bucks", "Ten Bucks", "Completed"])
                    
                elif error_type == "missing_value":
                    # Pandas will fill this with NaN, which you convert to None
                    writer.writerow([i, "2026-06-08", "", "Item", 1, 10.0, 10.0, "Completed"])

    print(f"Generated {num_rows} rows of pure chaos in {filename}")

if __name__ == "__main__":
    generate_chaos_csv()