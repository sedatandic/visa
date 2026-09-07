import React, { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { SiteLayout } from "./components/SiteLayout";
import { RequireAdmin } from "./components/AdminLayout";
import Home from "./pages/Home";
import VisaTypes from "./pages/VisaTypes";
import VisaGuide from "./pages/VisaGuide";
import Documents from "./pages/Documents";
import Services from "./pages/Services";
import Articles from "./pages/Articles";
import ArticleDetail from "./pages/ArticleDetail";
import Faq from "./pages/Faq";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Kvkk from "./pages/Kvkk";
import LegalTerms from "./pages/LegalTerms";
import Apply from "./pages/Apply";
import Track from "./pages/Track";
import MyAccount from "./pages/MyAccount";
import Esim from "./pages/Esim";
import Insurance from "./pages/Insurance";
import Cart from "./pages/Cart";
import Tours from "./pages/Tours";
import OrderStatus from "./pages/OrderStatus";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentCancel from "./pages/PaymentCancel";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import AdminApplicationDetail from "./pages/AdminApplicationDetail";
import AdminMessages from "./pages/AdminMessages";
import AdminEmails from "./pages/AdminEmails";
import AdminVisaTypes from "./pages/AdminVisaTypes";
import AdminVisaGuides from "./pages/AdminVisaGuides";
import AdminOrders from "./pages/AdminOrders";
import AdminInsurance from "./pages/AdminInsurance";
import AdminTestimonials from "./pages/AdminTestimonials";
import AdminArticles from "./pages/AdminArticles";
import AdminBankTransfer from "./pages/AdminBankTransfer";
import AdminCompany from "./pages/AdminCompany";
import AdminZami from "./pages/AdminZami";
import AdminWhatsApp from "./pages/AdminWhatsApp";
import AdminVisitors from "./pages/AdminVisitors";
import NotFound from "./pages/NotFound";
import "./App.css";

const ScrollToTop = () => {
    const { pathname } = useLocation();
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [pathname]);
    return null;
};

const Site = ({ children }) => <SiteLayout>{children}</SiteLayout>;

function App() {
    return (
        <div className="App">
            <BrowserRouter>
                <ScrollToTop />
                <Routes>
                    <Route path="/" element={<Site><Home /></Site>} />
                    <Route path="/vize-tipleri" element={<Site><VisaTypes /></Site>} />
                    <Route path="/dubai-vize-ucreti" element={<Navigate to="/vize-tipleri" replace />} />
                    <Route path="/dubai-vizesi/:slug" element={<Site><VisaGuide /></Site>} />
                    <Route path="/gerekli-belgeler" element={<Site><Documents /></Site>} />
                    <Route path="/hizmetler" element={<Site><Services /></Site>} />
                    <Route path="/gelismeler" element={<Site><Articles /></Site>} />
                    <Route path="/gelismeler/:slug" element={<Site><ArticleDetail /></Site>} />
                    <Route path="/sss" element={<Site><Faq /></Site>} />
                    <Route path="/hakkimizda" element={<Site><About /></Site>} />
                    <Route path="/iletisim" element={<Site><Contact /></Site>} />
                    <Route path="/kvkk" element={<Site><Kvkk /></Site>} />
                    <Route path="/iade-kosullari" element={<Site><LegalTerms variant="refund" /></Site>} />
                    <Route path="/hizmet-sozlesmesi" element={<Site><LegalTerms variant="service" /></Site>} />
                    <Route path="/gizlilik-politikasi" element={<Site><LegalTerms variant="privacy" /></Site>} />
                    <Route path="/ticari-ileti-onami" element={<Site><LegalTerms variant="marketing" /></Site>} />
                    <Route path="/basvuru" element={<Site><Apply /></Site>} />
                    <Route path="/takip" element={<Site><Track /></Site>} />
                    <Route path="/hesabim" element={<Site><MyAccount /></Site>} />
                    <Route path="/esim" element={<Site><Esim /></Site>} />
                    <Route path="/seyahat-sigortasi" element={<Site><Insurance /></Site>} />
                    <Route path="/sepet" element={<Site><Cart /></Site>} />
                    <Route path="/dubai-turlari" element={<Site><Tours /></Site>} />
                    <Route path="/siparis/:reference" element={<Site><OrderStatus /></Site>} />
                    <Route path="/odeme/basarili" element={<Site><PaymentSuccess /></Site>} />
                    <Route path="/odeme/iptal" element={<Site><PaymentCancel /></Site>} />

                    <Route path="/admin/giris" element={<AdminLogin />} />
                    <Route path="/admin" element={<RequireAdmin><AdminDashboard /></RequireAdmin>} />
                    <Route path="/admin/basvuru/:id" element={<RequireAdmin><AdminApplicationDetail /></RequireAdmin>} />
                    <Route path="/admin/mesajlar" element={<RequireAdmin><AdminMessages /></RequireAdmin>} />
                    <Route path="/admin/e-postalar" element={<RequireAdmin><AdminEmails /></RequireAdmin>} />
                    <Route path="/admin/vize-tipleri" element={<RequireAdmin><AdminVisaTypes /></RequireAdmin>} />
                    <Route path="/admin/vize-rehberleri" element={<RequireAdmin><AdminVisaGuides /></RequireAdmin>} />
                    <Route path="/admin/siparisler" element={<RequireAdmin><AdminOrders /></RequireAdmin>} />
                    <Route path="/admin/sigorta" element={<RequireAdmin><AdminInsurance /></RequireAdmin>} />
                    <Route path="/admin/yorumlar" element={<RequireAdmin><AdminTestimonials /></RequireAdmin>} />
                    <Route path="/admin/yazilar" element={<RequireAdmin><AdminArticles /></RequireAdmin>} />
                    <Route path="/admin/banka" element={<RequireAdmin><AdminBankTransfer /></RequireAdmin>} />
                    <Route path="/admin/acente" element={<RequireAdmin><AdminCompany /></RequireAdmin>} />
                    <Route path="/admin/zami" element={<RequireAdmin><AdminZami /></RequireAdmin>} />
                    <Route path="/admin/whatsapp" element={<RequireAdmin><AdminWhatsApp /></RequireAdmin>} />
                    <Route path="/admin/ziyaretciler" element={<RequireAdmin><AdminVisitors /></RequireAdmin>} />

                    <Route path="*" element={<Site><NotFound /></Site>} />
                </Routes>
                <Toaster position="bottom-right" closeButton />
            </BrowserRouter>
        </div>
    );
}

export default App;
