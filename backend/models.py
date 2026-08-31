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
    insurance_plus: bool = False
    esim: bool = False


class StoreItemIn(BaseModel):
    """Vize basvurusu icinde satin alinan eSIM / sigorta urunu."""

    product_id: str = Field(..., min_length=2, max_length=60)
    quantity: int = Field(1, ge=1, le=10)


class ExtraDocumentsIn(BaseModel):
    ticket_file_id: Optional[str] = None
    hotel_file_id: Optional[str] = None
    other_file_ids: List[str] = Field(default_factory=list)


class ApplicationCreate(BaseModel):
    contact: ContactIn
    travelers: List[TravelerIn] = Field(..., min_length=1, max_length=10)
    travel: TravelIn
    addons: AddonsIn = Field(default_factory=AddonsIn)
    store_items: List[StoreItemIn] = Field(default_factory=list, max_length=6)
    extra_documents: ExtraDocumentsIn = Field(default_factory=ExtraDocumentsIn)
    kvkk_accepted: bool = True


class TravelerDocumentIn(BaseModel):
    traveler_id: str = Field(..., min_length=4)
    passport_file_id: Optional[str] = None
    photo_file_id: Optional[str] = None


class DocumentSubmission(BaseModel):
    """Musterinin takip sayfasindan eksik belge yuklemesi."""

    last_name: str = Field(..., min_length=2, max_length=80)
    ticket_file_id: Optional[str] = None
    hotel_file_id: Optional[str] = None
    traveler_documents: List[TravelerDocumentIn] = Field(default_factory=list)


class QuoteRequest(BaseModel):
    visa_type_ids: List[str] = Field(..., min_length=1, max_length=10)
    addons: AddonsIn = Field(default_factory=AddonsIn)
    store_items: List[StoreItemIn] = Field(default_factory=list, max_length=6)
    # eSIM / sigorta gecerlilik tarihleri seyahat tarihlerine gore hesaplanir
    arrival_date: Optional[str] = Field(default=None, max_length=20)
    departure_date: Optional[str] = Field(default=None, max_length=20)


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


class TestimonialIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    initials: Optional[str] = Field(default="", max_length=4)
    city: Optional[str] = Field(default="", max_length=60)
    visa: Optional[str] = Field(default="", max_length=80)
    date: Optional[str] = Field(default="", max_length=20)
    text: str = Field(..., min_length=10, max_length=800)
    rating: int = Field(default=5, ge=1, le=5)
    verified: bool = True
    published: bool = True
    order: int = 0


class ReviewHighlightIn(BaseModel):
    label: str = Field(..., min_length=2, max_length=60)
    value: int = Field(..., ge=0, le=100)


class ReviewSummaryIn(BaseModel):
    average: float = Field(..., ge=0, le=5)
    total_reviews: int = Field(..., ge=0)
    total_applications: int = Field(..., ge=0)
    recommend_rate: int = Field(default=95, ge=0, le=100)
    highlights: List[ReviewHighlightIn] = Field(default_factory=list)


class ArticleIn(BaseModel):
    title: str = Field(..., min_length=5, max_length=160)
    slug: Optional[str] = Field(default="", max_length=160)
    date: Optional[str] = Field(default="", max_length=20)
    excerpt: str = Field(..., min_length=20, max_length=400)
    body: List[str] = Field(default_factory=list)
    cover_image: Optional[str] = Field(default="", max_length=500)
    published: bool = True
    order: int = 0


class BankTransferIn(BaseModel):
    enabled: bool = True
    title: str = Field(default="Havale / EFT ile ödeme", max_length=120)
    account_name: str = Field(..., min_length=2, max_length=160)
    bank_name: str = Field(..., min_length=2, max_length=120)
    iban: str = Field(..., min_length=10, max_length=40)
    currency: str = Field(default="TRY", max_length=5)
    note: Optional[str] = Field(default="", max_length=600)
    steps: List[str] = Field(default_factory=list)


class CompanyInfoIn(BaseModel):
    brand: Optional[str] = Field(default="", max_length=80)
    legal_name: str = Field(..., min_length=2, max_length=160)
    phone: Optional[str] = Field(default="", max_length=40)
    whatsapp: Optional[str] = Field(default="", max_length=30)
    email: Optional[str] = Field(default="", max_length=120)
    address: Optional[str] = Field(default="", max_length=240)
    working_hours: Optional[str] = Field(default="", max_length=160)
    tursab_no: Optional[str] = Field(default="", max_length=30)
    tursab_type: Optional[str] = Field(default="", max_length=80)
    tax_office: Optional[str] = Field(default="", max_length=80)
    tax_no: Optional[str] = Field(default="", max_length=30)
    mersis_no: Optional[str] = Field(default="", max_length=30)
    trade_registry_no: Optional[str] = Field(default="", max_length=30)
    founded_year: Optional[str] = Field(default="", max_length=10)


class WhatsAppRequest(BaseModel):
    template: str = Field(default="visa_ready", max_length=40)
    message: Optional[str] = Field(default="", max_length=1000)
    origin_url: Optional[str] = None
