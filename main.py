from fastapi import FastAPI,HTTPException,status,Depends
from data_schemas import ProductRequest,ProductResponse,SaleRequest,SaleRespone,Sales_detailRequest,Sales_detailResponse,PurchaseRequest,PurchaseResponse,PaymentRequest,PaymentResponse,RegisterRequest,RegisterResponse,LoginRequest,LoginResponse,CallbackResponse
from models import Base,Product,Sale,Sales_detail,Purchase,User,Payment
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from myjwt import verify_password,create_access_token,get_password_hash,get_current_user
from mpesa import make_stk_push
from generate_receipts import create_pdf

app = FastAPI()

engine = create_engine("sqlite:///./fastduka_api.db", echo=True)

Base.metadata.create_all(engine)

session = Session(engine)

# home route
@app.get("/")
def read_root():
    return {"FastAPI Version": "1.0"}
#End of home route

# Register route
@app.post("/register", response_model=RegisterResponse)
def register_user(user: RegisterRequest):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    query = select(User).where(User.email==user.email)
    dbuser = session.scalars(query).first()

    if dbuser:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    dbuser = User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        password=get_password_hash(user.password)
    )
    session.add(dbuser)
    session.commit()

    dbuser.token=create_access_token({"sub":dbuser.email})

    return dbuser

# login route
@app.post("/login", response_model=LoginResponse)
def login(user: LoginRequest):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # user = session.scalars(select(User).where(User.email==user.email)).first() ----- also correct
    query = select(User).where(User.email==user.email)
    dbuser = session.scalars(query).first()

    if not dbuser:
        raise credentials_exception
    
    if not verify_password(user.password, dbuser.password):
        raise credentials_exception

    dbuser.token=create_access_token({"sub":dbuser.email})
    return dbuser
# end of login route
    
# product routes
@app.post("/products", response_model=ProductResponse)
def create_product(prod: ProductRequest, current_user: str=Depends(get_current_user)):
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
def get_products(current_user: str=Depends(get_current_user) ):
    print("the current user is---------------",current_user)
    # getting data from database
    query = select(Product)
    products = session.scalars(query)
    
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_single_product(product_id : int):
    query = select(Product).where(Product.id == product_id)
    products = session.scalars(query).first()
    
    if products is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
            )

    return products

# path parameter(the one in curly braces) is useful when writing a query
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(prod : ProductRequest,product_id : int):
    query = select(Product).where(Product.id == product_id)
    products = session.scalars(query).first()

    if products is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    
    products.product_name = prod.product_name
    products.buying_price = prod.buying_price
    products.selling_price = prod.selling_price

    # session.add(dbprod) --- this is not needed since it si not a new product we are adding we are just updating an existing product 
    session.commit()
    
    return products
# End of product routes

# sales routes
@app.post("/sales", response_model=SaleRespone)
def create_sales(sal: SaleRequest, current_user: str=Depends(get_current_user)):
    dbsal = Sale(
        product_name=sal.product_name,
        amount=sal.amount
    )

    session.add(dbsal)
    session.commit()
    return dbsal

@app.get("/sales", response_model=list[SaleRespone])
def get_sales(current_user: str=Depends(get_current_user)):
    query = select(Sale)
    sales = session.scalars(query)

    return sales

@app.get("/sales/{sales_id}", response_model=SaleRespone)
def get_single_sale(sales_id : int):
    query = select(Sale).where(Sale.id == sales_id)
    sales = session.scalars(query).first()
    
    if sales is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    return sales

@app.put("/sales/{sales_id}", response_model=SaleRespone)
def update_sale(sal : SaleRequest, sales_id : int):
    query = select(Sale).where(Sale.id == sales_id)
    sales = session.scalars(query).first()

    if sales is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    sales.product_name = sal.product_name
    sales.amount = sal.amount

    session.commit()

    return sales
# End of sales routes

# sales_detail routes
@app.post("/sales_detail", response_model=Sales_detailResponse)
def create_sales_detail(sal_details: Sales_detailRequest, current_user: str=Depends(get_current_user)):
    dbsal_details = Sales_detail(
        product_id = sal_details.product_id,
        sales_id = sal_details.sales_id,
        quantity = sal_details.quantity
    )

    session.add(dbsal_details)
    session.commit()
    return dbsal_details

@app.get("/sales_details", response_model=list[Sales_detailResponse])
def get_sales_details(current_user: str=Depends(get_current_user)):
    query=select(Sales_detail)
    sales_details=session.scalars(query)

    return sales_details

@app.get("/sales_details/{sales_detail_id}", response_model=Sales_detailResponse)
def get_single_sale_detail(sales_detail_id : int):
    query = select(Sales_detail).where(Sales_detail.id == sales_detail_id)
    sales_detail = session.scalars(query).first()
    
    if sales_detail is None:
        raise HTTPException(
            status_code=404,
            detail="Sale_details not found"
        )

    return sales_detail

@app.put("/sales_details/{sales_detail_id}", response_model=Sales_detailResponse)
def update_sales_details(sal_details : Sales_detailRequest,sales_detail_id : int):
    query = select(Sales_detail).where(Sales_detail.id == sales_detail_id)
    sales_detail = session.scalars(query).first()
    
    if sales_detail is None:
        raise HTTPException(
            status_code=404,
            detail="Sale_details not found"
        )

    sales_detail.product_id = sal_details.product_id
    sales_detail.sales_id = sal_details.sales_id
    sales_detail.quantity = sal_details.quantity

    session.commit()

    return sales_detail
# End of sales_detail routes

# purchase routes
@app.post("/purchase", response_model=PurchaseResponse)
def create_purchase(purch: PurchaseRequest, current_user: str=Depends(get_current_user)):
    dbpurch = Purchase(
        product_id = purch.product_id,
        buying_price = purch.buying_price,
        quantity = purch.quantity
    )

    session.add(dbpurch)
    session.commit()
    return dbpurch

@app.get("/purchase", response_model=list[PurchaseResponse])
def get_purchases(current_user: str=Depends(get_current_user)):
    query=select(Purchase)
    purchases=session.scalars(query)

    return purchases

@app.get("/purchase/{purchase_id}", response_model=PurchaseResponse)
def get_single_purchase(purchase_id : int):
    query = select(Purchase).where(Purchase.id == purchase_id)
    purchase = session.scalars(query).first()

    if purchase is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )

    return purchase

@app.put("/purchase/{purchase_id}", response_model=PurchaseResponse)
def update_purchase(purch : PurchaseRequest, purchase_id : int):
    query = select(Purchase).where(Purchase.id == purchase_id)
    purchase = session.scalars(query).first()

    if purchase is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )

    purchase.product_id = purch.product_id
    purchase.buying_price = purch.buying_price
    purchase.quantity = purch.quantity

    session.commit()

    return purchase
# End of purchase routes

# payment routes
@app.post("/payment", response_model=PaymentResponse)
def create_payment(pay: PaymentRequest, current_user: str=Depends(get_current_user)):
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
def get_payment(current_user: str=Depends(get_current_user)):
    query=select(Payment)
    payments=session.scalars(query)

    return payments

@app.get("/payment/{payment_id}", response_model=PaymentResponse)
def get_single_paymnet(payment_id : int):
    query = select(Payment).where(Payment.id == payment_id)
    payment = session.scalars(query).first()
    
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment

@app.put("/payment/{payment_id}", response_model=PaymentResponse)
def update_payment(pay : PaymentRequest, payment_id : int):
    query = select(Payment).where(Payment.id == payment_id)
    payment = session.scalars(query).first()
    
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    payment.sales_id = pay.sales_id
    payment.amount = pay.amount
    payment.transaction_code = pay.transaction_code
    payment.mrid = pay.mrid
    payment.crid = pay.crid
    payment.payment_status = pay.payment_status
    payment.phone_number = pay.phone_number

    session.commit()

    return payment
# End of payment routes

# stk-push route
# @app.post("/stk_push", response_model=PaymentResponse)
# def make_stk_push(pay : PaymentRequest):
#     dbpush = Payment(
#         sales_id = pay.sales_id,
#         amount = pay.amount,
#         transaction_code = pay.transaction_code,
#         mrid = pay.mrid,
#         crid = pay.crid,
#         payment_status = pay.payment_status,
#         phone_number = pay.phone_number
#     )
    
#     session.add(dbpush)
#     session.commit()
#     return dbpush


@app.post("/stk_push", response_model=PaymentResponse)
def stk_push(payload: PaymentRequest):
    try:
        response = make_stk_push({
            "sales_id": payload.sales_id,
            "amount": payload.amount,
            "phone_number": payload.phone_number,
        })

        new_payment = Payment(
            sales_id=payload.sales_id,
            amount=payload.amount,
            phone_number=payload.phone_number,
            mrid=response.get("MerchantRequestID"),
            crid=response.get("CheckoutRequestID"),
            transaction_code=None,
            payment_status="pending",
        )

        session.add(new_payment)
        session.commit()

        return new_payment

    except Exception as e:
        # session.rollback() cancels any database changes that haven’t been committed
        session.rollback()
        print(f"stk push error: {e}")
        raise HTTPException(status_code=500, detail="STK push failed")

@app.post("/saf-callback", response_model=CallbackResponse)
def saf_callback(payload: dict):
    try:
        body = payload.get("Body", {})
        stk_callback = body.get("stkCallback", {})

        result_code = stk_callback.get("ResultCode")
        mrid = stk_callback.get("MerchantRequestID")
        crid = stk_callback.get("CheckoutRequestID")

        payment = session.scalars(
            select(Payment).where(
                Payment.mrid == mrid,
                Payment.crid == crid,
            )
        ).first()

        if payment:
            if result_code == 0:
                callback_metadata = (
                    stk_callback.get("CallbackMetadata", {}).get("Item", [])
                )

                for item in callback_metadata:
                    if item.get("Name") == "MpesaReceiptNumber":
                        payment.transaction_code = item.get("Value")

                payment.payment_status = "complete"

                session.commit()

                text = (
                    f"Trans Code: {payment.transaction_code}, "
                    f"Amount: {payment.amount}, "
                    f"Date: {payment.payment_date}"
                )
                create_pdf(text, payment.transaction_code)
            else:
                payment.payment_status = "failed"
                session.commit()

    except Exception as e:
        print(f"Error for callback: {e}")
        session.rollback()

    return {"message": "callback received"}