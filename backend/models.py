import re
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactIn(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=25)
    address_city: Optional[str] = Field(default="", max_length=60)
    whatsapp_optin: bool = False


def _iso_date_or_error(value: str, label: str) -> str:
    """Tarih dogrulamasi: ISO (YYYY-MM-DD) ve GG.AA.YYYY kabul edilir, ISO'ya cevrilir."""
    text = (value or "").strip()
    dotted = re.fullmatch(r"(\d{2})[.\-/](\d{2})[.\-/](\d{4})", text)
    if dotted:
        day, month, year = dotted.groups()
        text = f"{year}-{month}-{day}"
    text = text[:10]
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"{label} GG.AA.YYYY olarak eksiksiz girilmelidir")
    return text


class TravelerIn(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name: str = Field(..., min_length=2, max_length=60)
    birth_date: str = Field(..., min_length=4, max_length=20)
    # Cinsiyet basvuru formunda sorulmaz; pasaport MRZ'sinden (OCR) okunur.
    # Okunamazsa bos gelir ve Zami aktarimi oncesi admin tamamlar.
    gender: str = Field(default="", pattern="^(male|female|)$")
    applicant_type: str = Field(default="adult", pattern="^(adult|child)$")
    nationality: str = Field(default="TR", max_length=40)
    national_id: Optional[str] = Field(default="", max_length=20)
    passport_no: str = Field(..., min_length=4, max_length=20)
    passport_expiry: str = Field(..., min_length=4, max_length=20)
    # Pasaport OCR'dan otomatik gelen ek alanlar (kullaniciya soru sorulmaz).
    # Zami formunda zorunlu olduklari icin aktarimda kullanilir.
    passport_issue_date: Optional[str] = Field(default="", max_length=20)
    birth_place: Optional[str] = Field(default="", max_length=60)
    passport_issue_place: Optional[str] = Field(default="", max_length=60)
    # Zami formunda zorunlu olan ve basvuru formunda kullaniciya sorulan alanlar
    marital_status: str = Field(default="single", pattern="^(single|married|divorced|widowed)$")
    profession: str = Field(default="", max_length=60)
    mother_name: str = Field(default="", max_length=80)
    father_name: str = Field(default="", max_length=80)
    visa_type_id: str = Field(..., min_length=3)
    # Sigorta satin alinirsa police kesimi icin zorunlu (Tamamliyo API'si TC kimlik istiyor)
    tc_kimlik_no: Optional[str] = Field(default="", max_length=11)
    passport_file_id: str = Field(..., min_length=8)
    photo_file_id: str = Field(..., min_length=8)

    @field_validator("birth_date")
    @classmethod
    def _check_birth_date(cls, value: str) -> str:
        return _iso_date_or_error(value, "Doğum tarihi")

    @field_validator("passport_expiry")
    @classmethod
    def _check_passport_expiry(cls, value: str) -> str:
        return _iso_date_or_error(value, "Pasaport geçerlilik tarihi")


class TravelIn(BaseModel):
    # Tarihi henuz belli olmayan basvurularda tarihler bos gelir, aralik secimi alinir
    arrival_date: str = Field(default="", max_length=20)
    departure_date: str = Field(default="", max_length=20)
    dates_unknown: bool = False
    travel_window: Optional[str] = Field(default="", max_length=30)
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
    # Tur urunleri icin secilen tur tarihi / baslangic saati
    scheduled_date: Optional[str] = Field(None, max_length=10)
    scheduled_time: Optional[str] = Field(None, max_length=5)


class InsuredIn(BaseModel):
    """Sigorta policesi icin sigortali kisi (Tamamliyo TC kimlik + dogum tarihi ister)."""

    full_name: str = Field(..., min_length=3, max_length=90)
    tc_kimlik_no: str = Field(..., min_length=11, max_length=11)
    birth_date: str = Field(..., min_length=8, max_length=10)

    @field_validator("tc_kimlik_no")
    @classmethod
    def _check_tckn(cls, value: str) -> str:
        from tckn import clean_tckn, valid_tckn

        digits = clean_tckn(value)
        if not valid_tckn(digits):
            raise ValueError("Geçerli bir TC kimlik numarası girin.")
        return digits

    @field_validator("birth_date")
    @classmethod
    def _check_birth(cls, value: str) -> str:
        return _iso_date_or_error(value, "Doğum tarihi")


class ExtraDocumentsIn(BaseModel):
    ticket_file_id: Optional[str] = None
    hotel_file_id: Optional[str] = None
    other_file_ids: List[str] = Field(default_factory=list)


class ConsentsIn(BaseModel):
    refund_privacy_accepted: bool = False
    service_terms_accepted: bool = False
    marketing_email_optin: bool = False
    ad_personalization_optin: bool = False


class ApplicationCreate(BaseModel):
    contact: ContactIn
    travelers: List[TravelerIn] = Field(..., min_length=1, max_length=10)
    travel: TravelIn
    addons: AddonsIn = Field(default_factory=AddonsIn)
    store_items: List[StoreItemIn] = Field(default_factory=list, max_length=6)
    extra_documents: ExtraDocumentsIn = Field(default_factory=ExtraDocumentsIn)
    kvkk_accepted: bool = True
    consents: ConsentsIn = Field(default_factory=ConsentsIn)
    # Yonetici teklif linkinden gelindiyse donusum takibi icin tasinir
    offer_token: Optional[str] = Field(default="", max_length=40)


class OfferTravelerIn(BaseModel):
    applicant_type: str = Field(default="adult", pattern="^(adult|child)$")
    visa_type_id: str = Field(..., min_length=3, max_length=60)


class OfferLinkIn(BaseModel):
    """Yoneticinin hazirladigi, WhatsApp ile paylasilabilir teklif."""

    title: Optional[str] = Field(default="", max_length=120)
    customer_name: Optional[str] = Field(default="", max_length=120)
    customer_phone: Optional[str] = Field(default="", max_length=25)
    customer_email: Optional[str] = Field(default="", max_length=120)
    travelers: List[OfferTravelerIn] = Field(..., min_length=1, max_length=10)
    addons: AddonsIn = Field(default_factory=AddonsIn)
    store_items: List[StoreItemIn] = Field(default_factory=list, max_length=6)
    arrival_date: Optional[str] = Field(default="", max_length=20)
    departure_date: Optional[str] = Field(default="", max_length=20)
    note: Optional[str] = Field(default="", max_length=600)
    valid_days: int = Field(default=14, ge=1, le=90)


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


class AdminCodeRequest(BaseModel):
    """Yonetici girisi: e-postaya tek kullanimlik kod talebi."""

    email: EmailStr


class AdminCodeVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


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


class VisitIn(BaseModel):
    path: str = Field(default="/", max_length=300)
    referrer: str = Field(default="", max_length=300)


class BankAccountIn(BaseModel):
    currency: str = Field(default="TRY", max_length=5)
    iban: str = Field(..., min_length=10, max_length=40)


class BankIn(BaseModel):
    id: Optional[str] = Field(default="", max_length=40)
    name: str = Field(..., min_length=2, max_length=120)
    logo: Optional[str] = Field(default="", max_length=300)
    accounts: List[BankAccountIn] = Field(default_factory=list)


class BankTransferIn(BaseModel):
    enabled: bool = True
    title: str = Field(default="Havale / EFT ile ödeme", max_length=120)
    account_name: str = Field(..., min_length=2, max_length=160)
    bank_name: str = Field(default="", max_length=120)
    iban: str = Field(default="", max_length=40)
    currency: str = Field(default="TRY", max_length=5)
    note: Optional[str] = Field(default="", max_length=600)
    notes: List[str] = Field(default_factory=list)
    banks: List[BankIn] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)


class CompanyInfoIn(BaseModel):
    brand: Optional[str] = Field(default="", max_length=80)
    legal_name: str = Field(..., min_length=2, max_length=160)
    phone: Optional[str] = Field(default="", max_length=40)
    whatsapp: Optional[str] = Field(default="", max_length=30)
    email: Optional[str] = Field(default="", max_length=120)
    instagram: Optional[str] = Field(default="", max_length=200)
    google_review: Optional[str] = Field(default="", max_length=300)
    address: Optional[str] = Field(default="", max_length=240)
    dubai_address: Optional[str] = Field(default="", max_length=240)
    dubai_phone: Optional[str] = Field(default="", max_length=40)
    working_hours: Optional[str] = Field(default="", max_length=160)
    tursab_no: Optional[str] = Field(default="", max_length=30)
    tursab_type: Optional[str] = Field(default="", max_length=80)
    tax_office: Optional[str] = Field(default="", max_length=80)
    tax_no: Optional[str] = Field(default="", max_length=30)
    mersis_no: Optional[str] = Field(default="", max_length=30)
    trade_registry_no: Optional[str] = Field(default="", max_length=30)
    founded_year: Optional[str] = Field(default="", max_length=10)


class SocialLinkIn(BaseModel):
    platform: str = Field(..., max_length=30)
    url: Optional[str] = Field(default="", max_length=400)
    enabled: bool = True
    in_dock: bool = True
    in_footer: bool = True
    in_contact: bool = True
    order: int = Field(default=0, ge=0, le=99)


class SocialLinksIn(BaseModel):
    items: List[SocialLinkIn] = Field(default_factory=list)


class InstagramPostIn(BaseModel):
    id: str = Field(..., max_length=20)
    scheduled_at: Optional[str] = Field(default=None, max_length=40)
    caption: Optional[str] = Field(default=None, max_length=2500)
    status: str = Field(default="planned", max_length=12)


class InstagramPlanIn(BaseModel):
    items: List[InstagramPostIn] = Field(default_factory=list)


class WhatsAppRequest(BaseModel):
    template: str = Field(default="visa_ready", max_length=40)
    message: Optional[str] = Field(default="", max_length=1000)
    origin_url: Optional[str] = None

