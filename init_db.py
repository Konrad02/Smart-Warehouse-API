from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/warehouse"

engine = create_engine(DATABASE_URL)

def populate_data():
    with engine.connect() as connection:
        print("🔌 Połączono z bazą danych!")
        
        trans = connection.begin()
        try:
            print("📦 Dodawanie kategorii...")
            connection.execute(text("""
                INSERT INTO categories (name, description) VALUES 
                ('Elektronika', 'Sprzęt elektroniczny i gadżety'),
                ('Narzędzia', 'Narzędzia warsztatowe i ogrodowe')
                ON CONFLICT (name) DO NOTHING;
            """))

            print("🍎 Dodawanie produktów...")
            connection.execute(text("""
                INSERT INTO products (name, sku, category_id, price, stock_quantity) 
                VALUES 
                ('iPhone 15', 'APP-IP15', (SELECT id FROM categories WHERE name='Elektronika'), 3999.00, 10),
                ('MacBook Pro', 'APP-MBP', (SELECT id FROM categories WHERE name='Elektronika'), 8500.00, 5),
                ('Wiertarka Bosch', 'BSC-DRILL', (SELECT id FROM categories WHERE name='Narzędzia'), 450.00, 20)
                ON CONFLICT (sku) DO NOTHING;
            """))
            
            trans.commit()
            print("✅ Sukces! Dane zostały dodane.")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    populate_data()