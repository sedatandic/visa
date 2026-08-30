import React, { useEffect } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { SiteLayout } from "./components/SiteLayout";
import { RequireAdmin } from "./components/AdminLayout";
import Home from "./pages/Home";
import VisaTypes from "./pages/VisaTypes";
import Documents from "./pages/Documents";
import Faq from "./pages/Faq";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Kvkk from "./pages/Kvkk";
import Apply from "./pages/Apply";
import Track from "./pages/Track";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentCancel from "./pages/PaymentCancel";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import AdminApplicationDetail from "./pages/AdminApplicationDetail";
import AdminMessages from "./pages/AdminMessages";
import AdminEmails from "./pages/AdminEmails";
import AdminVisaTypes from "./pages/AdminVisaTypes";
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
                    <Route path="/gerekli-belgeler" element={<Site><Documents /></Site>} />
                    <Route path="/sss" element={<Site><Faq /></Site>} />
                    <Route path="/hakkimizda" element={<Site><About /></Site>} />
                    <Route path="/iletisim" element={<Site><Contact /></Site>} />
                    <Route path="/kvkk" element={<Site><Kvkk /></Site>} />
                    <Route path="/basvuru" element={<Site><Apply /></Site>} />
                    <Route path="/takip" element={<Site><Track /></Site>} />
                    <Route path="/odeme/basarili" element={<Site><PaymentSuccess /></Site>} />
                    <Route path="/odeme/iptal" element={<Site><PaymentCancel /></Site>} />

                    <Route path="/admin/giris" element={<AdminLogin />} />
                    <Route
                        path="/admin"
                        element={
                            <RequireAdmin>
                                <AdminDashboard />
                            </RequireAdmin>
                        }
                    />
                    <Route
                        path="/admin/basvuru/:id"
                        element={
                            <RequireAdmin>
                                <AdminApplicationDetail />
                            </RequireAdmin>
                        }
                    />
                    <Route
                        path="/admin/mesajlar"
                        element={
                            <RequireAdmin>
                                <AdminMessages />
                            </RequireAdmin>
                        }
                    />
                    <Route
                        path="/admin/e-postalar"
                        element={
                            <RequireAdmin>
                                <AdminEmails />
                            </RequireAdmin>
                        }
                    />
                    <Route
                        path="/admin/vize-tipleri"
                        element={
                            <RequireAdmin>
                                <AdminVisaTypes />
                            </RequireAdmin>
                        }
                    />

                    <Route path="*" element={<Site><NotFound /></Site>} />
                </Routes>
                <Toaster position="top-center" richColors />
            </BrowserRouter>
        </div>
    );
}

export default App;
