from fastapi import FastAPI
from data_schemas import ProductRequest,ProductResponse,SaleRequest,SaleRespone,Sales_detailRequest,Sales_detailResponse,PurchaseRequest,PurchaseResponse,PaymentRequest,PaymentResponse
from models import Base,Product,Sale,Sales_detail,Purchase,User,Payment
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session

app = FastAPI()

engine = create_engine("sqlite:///./fastduka_api.db", echo=True)

Base.metadata.create_all(engine)

session = Session(engine)

# def add_user():
#     user = User(
#         full_name = "binti",
#         email = "binti@gmail.com",
#         password = "1234",
#         phone_number = "0700998865"
#         )
    
#     session.add(user)
#     session.commit()

# add_user()

# home route
@app.get("/")
def read_root():
    return {"FastAPI Version": "1.0"}

# product routes
@app.post("/products", response_model=ProductResponse)
def create_product(prod: ProductRequest):
    # store in the database
    dbprod = Product(
        user_id=prod.user_id,  
        product_name=prod.product_name,
        buying_price=prod.buying_price,
        selling_price=prod.selling_price,
    )

    session.add(dbprod)
    session.commit()
    return dbprod

@app.get("/products", response_model=list[ProductResponse])
def get_products():
    query = select(Product)
    products = session.scalars(query)
    
    return products

# sales routes
@app.post("/sales", response_model=SaleRespone)
def create_sales(sal: SaleRequest):
    dbsal = Sale(
        product_name=sal.product_name,
        amount=sal.amount
    )

    session.add(dbsal)
    session.commit()
    return dbsal

@app.get("/sales", response_model=list[SaleRespone])
def get_sales():
    query = select(Sale)
    sales = session.scalars(query)

    return sales

# sales_detail routes
@app.post("/sales_detail", response_model=Sales_detailResponse)
def create_sales_detail(sal_details: Sales_detailRequest):
    dbsal_details = Sales_detail(
        product_id = sal_details.product_id,
        sales_id = sal_details.sales_id,
        quantity = sal_details.quantity
    )

    session.add(dbsal_details)
    session.commit()
    return dbsal_details

@app.get("/sales_details", response_model=list[Sales_detailResponse])
def get_sales_details():
    query=select(Sales_detail)
    sales_details=session.scalars(query)

    return sales_details

# purchase routes
@app.post("/purchase", response_model=PurchaseResponse)
def create_purchase(purch: PurchaseRequest):
    dbpurch = Purchase(
        product_id = purch.product_id,
        buying_price = purch.buying_price,
        quantity = purch.quantity
    )

    session.add(dbpurch)
    session.commit()
    return dbpurch

@app.get("/purchase", response_model=list[PurchaseResponse])
def get_purchases():
    query=select(Purchase)
    purchases=session.scalars(query)

    return purchases

# payment routes
@app.post("/payment", response_model=PaymentResponse)
def create_payment(pay: PaymentRequest):
    dbpay = Payment(
        sales_id = pay.sales_id,
        amount = pay.amount,
        transaction_code = pay.transaction_code,
        mrid = pay.mrid,
        crid = pay.crid,
        payment_status = pay.payment_status,
        phone_number = pay.phone_number
    )

    session.add(dbpay)
    session.commit()
    return dbpay

@app.get("/payment", response_model=list[PaymentResponse])
def get_payment():
    query=select(Payment)
    payments=session.scalars(query)

    return payments