from fastapi import FastAPI
from data_schemas import ProductRequest,ProductResponse
from models import Base,Product
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = FastAPI()

engine = create_engine("sqlite:///./fastduka_api.db", echo=True)

Base.metadata.create_all(engine)

session = Session(engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.post("/products")
# def create_product(prod : ProductRequest):
#     # store in the database
#     dbprod = Product(
#         name=prod.product_name,
#         buying_price=prod.buying_price,
#         selling_price=prod.selling_price
#         )
    
#     session.add(dbprod)
#     session.commit()
#     session.refresh(dbprod)
#     return {"test" : "prod"}

@app.post("/products", response_model=ProductResponse)
def create_product(prod: ProductRequest):
    dbprod = Product(
        name=prod.product_name,
        buying_price=prod.buying_price,
        selling_price=prod.selling_price,
    )
    session.add(dbprod)
    session.commit()
    session.refresh(dbprod)
    return dbprod
