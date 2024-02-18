from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError


class Option(BaseModel):
    colors: List[str]
    sizes: List[str]


class Product(BaseModel):
    name: str
    sku: str
    price: float
    final_price: float
    options: Option
