from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ContactIn(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=25)
    address_city: Optional[str] = Field(default="", max_length=60)


class TravelerIn(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name: str = Field(..., min_length=2, max_length=60)
    birth_date: str = Field(..., min_length=4, max_length=20)
    gender: str = Field(..., pattern="^(male|female)$")
    applicant_type: str = Field(default="adult", pattern="^(adult|child)$")
    nationality: str = Field(default="TR", max_length=40)
    national_id: Optional[str] = Field(default="", max_length=20)
    passport_no: str = Field(..., min_length=4, max_length=20)
    passport_expiry: str = Field(..., min_length=4, max_length=20)
    visa_type_id: str = Field(..., min_length=3)
    passport_file_id: str = Field(..., min_length=8)
    photo_file_id: str = Field(..., min_length=8)


class TravelIn(BaseModel):
    arrival_date: str = Field(..., min_length=4, max_length=20)
    departure_date: str = Field(..., min_length=4, max_length=20)
    purpose: str = Field(default="tourism", max_length=30)
    birth_country: Optional[str] = Field(default="TR", max_length=40)
    accommodation: Optional[str] = Field(default="", max_length=200)
    flight_no: Optional[str] = Field(default="", max_length=40)
    notes: Optional[str] = Field(default="", max_length=1000)


class AddonsIn(BaseModel):
    express: bool = False
    insurance: bool = False


class ExtraDocumentsIn(BaseModel):
    ticket_file_id: Optional[str] = None
    hotel_file_id: Optional[str] = None
    other_file_ids: List[str] = Field(default_factory=list)


class ApplicationCreate(BaseModel):
    contact: ContactIn
    travelers: List[TravelerIn] = Field(..., min_length=1, max_length=10)
    travel: TravelIn
    addons: AddonsIn = Field(default_factory=AddonsIn)
    extra_documents: ExtraDocumentsIn = Field(default_factory=ExtraDocumentsIn)
    kvkk_accepted: bool = True


class QuoteRequest(BaseModel):
    visa_type_ids: List[str] = Field(..., min_length=1, max_length=10)
    addons: AddonsIn = Field(default_factory=AddonsIn)


class CheckoutRequest(BaseModel):
    application_id: str
    origin_url: str


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    phone: Optional[str] = Field(default="", max_length=25)
    subject: Optional[str] = Field(default="", max_length=120)
    message: str = Field(..., min_length=5, max_length=2000)


class AdminLogin(BaseModel):
    email: str
    password: str


class StatusUpdate(BaseModel):
    status: str
    note: Optional[str] = ""
    notify: bool = True


class SendVisaRequest(BaseModel):
    origin_url: Optional[str] = None
    message: Optional[str] = ""
    set_approved: bool = True
