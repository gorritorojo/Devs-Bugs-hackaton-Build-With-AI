from pydantic import BaseModel, Field


class RegisterUser(BaseModel):
    role: str
    contact_name: str | None = Field(default=None, alias="contactName")
    email: str | None = None
    company_name: str | None = Field(default=None, alias="companyName")
    phone: str | None = None

    model_config = {"populate_by_name": True}


class LoginUser(BaseModel):
    role: str
    email: str | None = None
    phone: str | None = None


class UpdateProfile(BaseModel):
    area: str | None = None
    products: str | None = None
    business_size: str | None = Field(default=None, alias="businessSize")

    model_config = {"populate_by_name": True}


class CreateLot(BaseModel):
    product: str
    producer: str
    target_kilos: float = Field(alias="targetKilos")
    base_price: float = Field(alias="basePrice")
    deadline: str
    created_by: str | None = Field(default=None, alias="createdBy")

    model_config = {"populate_by_name": True}


class CommitLot(BaseModel):
    kilos: float
    user_id: str | None = Field(default=None, alias="userId")


class UpdateLotStatus(BaseModel):
    status: str
    user_id: str = Field(alias="userId")

    model_config = {"populate_by_name": True}
