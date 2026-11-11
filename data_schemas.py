# Rules to follow in the schema class
# Ensure your request data contains all fields from model class excluding id and created_at
# Ensure all fields in the model class are in your schema response class
# Avoid any naming issues,have model class fields and schema class fields exactly the same


from pydantic import BaseModel
from datetime import datetime

class ProductRequest(BaseModel):
    user_id : int
    product_name : str
    buying_price : float
    selling_price : float

class ProductResponse(BaseModel):
    id : int
    user_id : int
    product_name : str
    buying_price : float
    selling_price : float
    created_at : datetime

class SaleRequest(BaseModel):
    product_name : str
    amount : float

class SaleRespone(BaseModel):
    id : int
    product_name : str
    amount : float
    sale_date : datetime

class Sales_detailRequest(BaseModel):
    product_id : int
    sales_id : int
    quantity : float

class Sales_detailResponse(BaseModel):
    id : int
    product_id : int
    sales_id : int
    quantity : float

class PurchaseRequest(BaseModel):
    product_id : int
    quantity : float
    buying_price : float

class PurchaseResponse(BaseModel):
    id : int
    product_id : int
    quantity : float
    buying_price : float
    purchase_date : datetime

class PaymentRequest(BaseModel):
    sales_id : int
    amount : float
    transaction_code: str
    mrid: str
    crid: str
    payment_status : str
    phone_number: int

class PaymentResponse(BaseModel):
    id : int
    sales_id : int
    amount : float
    transaction_code: str
    mrid: str
    crid: str
    payment_status : str
    phone_number: int
    payment_date: datetime



