from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, text
from typing import Literal

DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/warehouse"
engine = create_engine(DATABASE_URL)

app = FastAPI(title="Smart Warehouse API")

class ProductCreate(BaseModel):
    name: str
    sku: str
    category_id: int
    price: float
    stock_quantity: int

class MovementCreate(BaseModel):
    product_id: int
    movement_type: Literal['IN', 'OUT']
    quantity: int
    contractor_id: int | None = None

    @field_validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Ilość musi być większa od zera")
        return v

@app.get("/")
def read_root():
    return {"message": "System magazynowy działa!"}

@app.get("/products")
def get_products():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM products ORDER BY id"))
        return [dict(row._mapping) for row in result]
    
@app.post("/products")
def create_product(product: ProductCreate):
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            query = text("""
                INSERT INTO products (name, sku, category_id, price, stock_quantity)
                VALUES (:name, :sku, :category_id, :price, :stock_quantity)
                RETURNING id, name
            """)
            result = connection.execute(query, {
                "name": product.name,
                "sku": product.sku,
                "category_id": product.category_id,
                "price": product.price,
                "stock_quantity": product.stock_quantity
            })
            trans.commit()
            new_product = result.fetchone()
            return {"status": "created", "product_id": new_product.id, "name": new_product.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Błąd przy dodawaniu produktu. Sprawdź czy kategoria istnieje i SKU jest unikalne.")

@app.post("/movements")
def create_movement(movement: MovementCreate):
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            result = connection.execute(text("SELECT stock_quantity FROM products WHERE id = :id"), {"id": movement.product_id})
            product = result.fetchone()
            
            if not product:
                raise HTTPException(status_code=404, detail="Produkt nie istnieje")
            
            current_stock = product.stock_quantity

            new_stock = current_stock
            
            if movement.movement_type == 'OUT':
                if current_stock < movement.quantity:
                    raise HTTPException(status_code=400, detail=f"Brak towaru! Stan: {current_stock}, Chcesz wydać: {movement.quantity}")
                new_stock = current_stock - movement.quantity
            elif movement.movement_type == 'IN':
                new_stock = current_stock + movement.quantity

            connection.execute(text("""
                INSERT INTO movements (product_id, movement_type, quantity)
                VALUES (:pid, :type, :qty)
            """), {"pid": movement.product_id, "type": movement.movement_type, "qty": movement.quantity})

            connection.execute(text("""
                UPDATE products SET stock_quantity = :new_stock WHERE id = :pid
            """), {"new_stock": new_stock, "pid": movement.product_id})

            trans.commit()
            return {"message": "Ruch zapisany", "new_stock": new_stock}

        except HTTPException as he:
            trans.rollback()
            raise he
        except Exception as e:
            trans.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/stats")
def get_warehouse_stats():
    with engine.connect() as connection:
        total_value_query = text("SELECT COALESCE(SUM(price * stock_quantity), 0) FROM products")
        total_value = connection.execute(total_value_query).scalar()
        
        low_stock_query = text("SELECT name, stock_quantity FROM products WHERE stock_quantity < 10")
        low_stock_result = connection.execute(low_stock_query)
        low_stock_products = [dict(row._mapping) for row in low_stock_result]
        
        return {
            "total_inventory_value_pln": total_value,
            "low_stock_alerts": low_stock_products,
            "alert_count": len(low_stock_products)
        }