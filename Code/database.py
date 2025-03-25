import sqlite3
import csv

# Path to your CSV file
csv_file = 'Route Data.csv'

# Connect to the SQLite database
conn = sqlite3.connect('climbing_routes.db')
cursor = conn.cursor()

# Function to clear all rows in the routes table (keeping the table structure)
def clear_existing_data():
    cursor.execute('DELETE FROM routes')
    conn.commit()

# Clear the existing data before importing new data
clear_existing_data()

# Open and read the CSV file
with open(csv_file, 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)  # Skip the header row if your CSV has one

    # Insert each row of data into the database
    for row in csv_reader:
        if len(row) == 3:  # Ensure each row has 3 columns (name, difficulty, style)
            try:
                cursor.execute('''
                    INSERT INTO routes (name, difficulty, style)
                    VALUES (?, ?, ?)
                ''', row)
            except sqlite3.Error as e:
                print(f"Error inserting row {row}: {e}")

# Commit the changes and close the connection
try:
    conn.commit()
    print("Routes imported successfully!")
except sqlite3.Error as e:
    print(f"Error committing to database: {e}")
finally:
    conn.close()
