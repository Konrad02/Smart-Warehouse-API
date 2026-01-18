from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/warehouse"

engine = create_engine(DATABASE_URL)

def populate_data():
    with engine.connect() as connection:
        
        trans = connection.begin()
        try:
            connection.execute(text("""
                INSERT INTO categories (name, description) VALUES 
                ('Elektronika', 'Sprzęt elektroniczny i gadżety'),
                ('Narzędzia', 'Narzędzia warsztatowe i ogrodowe')
                ON CONFLICT (name) DO NOTHING;
            """))

            connection.execute(text("""
                INSERT INTO products (name, sku, category_id, price, stock_quantity) 
                VALUES 
                ('iPhone 15', 'APP-IP15', (SELECT id FROM categories WHERE name='Elektronika'), 3999.00, 10),
                ('MacBook Pro', 'APP-MBP', (SELECT id FROM categories WHERE name='Elektronika'), 8500.00, 5),
                ('Wiertarka Bosch', 'BSC-DRILL', (SELECT id FROM categories WHERE name='Narzędzia'), 450.00, 20)
                ON CONFLICT (sku) DO NOTHING;
            """))
            
            trans.commit()
            
        except Exception as e:
            trans.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    populate_data()