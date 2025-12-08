import sqlite3

# Connect to your database
conn = sqlite3.connect('instance/barangay.db')  # Adjust path if needed
cursor = conn.cursor()

try:
    # Add the missing columns
    cursor.execute('ALTER TABLE admin ADD COLUMN full_name VARCHAR(200)')
    print("✓ Added full_name column")
except sqlite3.OperationalError as e:
    print(f"full_name column might already exist: {e}")

try:
    cursor.execute('ALTER TABLE admin ADD COLUMN contact_number VARCHAR(20)')
    print("✓ Added contact_number column")
except sqlite3.OperationalError as e:
    print(f"contact_number column might already exist: {e}")

conn.commit()
conn.close()

print("\n✓ Database updated successfully!")
print("Try running your app again.")