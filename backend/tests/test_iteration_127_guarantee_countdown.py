"""36 saat garantisi durum makinesi: build_guarantee_status tum hallerini kapsar."""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/app/backend")

from routes_public import GUARANTEE_HOURS, build_guarantee_status  # noqa: E402

NOW = datetime.now(timezone.utc)


def doc(status="reviewing", history=None, transferred=None):
    return {
        "status": status,
        "status_history": history or [],
        "zami_transferred_at": transferred,
    }


def entry(status, at):
    return {"status": status, "at": at.isoformat()}


def test_sure_baslamadi_pending():
    info = build_guarantee_status(doc("submitted", [entry("submitted", NOW)]))
    assert info["state"] == "pending"
    assert info["hours"] == GUARANTEE_HOURS
    assert info["start_at"] is None
    assert info["deadline_at"] is None


def test_reviewing_ile_baslar_ve_isler():
    start = NOW - timedelta(hours=5)
    info = build_guarantee_status(doc("reviewing", [entry("reviewing", start)]))
    assert info["state"] == "running"
    assert info["remaining_seconds"] > 0
    assert info["deadline_at"].startswith((start + timedelta(hours=36)).isoformat()[:16])


def test_portal_aktarimi_da_sureyi_baslatir():
    start = NOW - timedelta(hours=2)
    info = build_guarantee_status(doc("submitted", [], transferred=start.isoformat()))
    assert info["state"] == "running"
    assert info["start_at"] == start.isoformat()


def test_sure_asilirsa_overdue():
    start = NOW - timedelta(hours=40)
    info = build_guarantee_status(doc("reviewing", [entry("reviewing", start)]))
    assert info["state"] == "overdue"
    assert info["remaining_seconds"] < 0


def test_suresinde_sonuclandi_met():
    start = NOW - timedelta(hours=30)
    done = NOW - timedelta(hours=2)
    info = build_guarantee_status(
        doc("approved", [entry("reviewing", start), entry("approved", done)])
    )
    assert info["state"] == "met"
    assert info["finished_at"] == done.isoformat()


def test_sure_asildiktan_sonra_sonuclandi_missed():
    start = NOW - timedelta(hours=50)
    done = NOW - timedelta(hours=1)
    info = build_guarantee_status(
        doc("approved", [entry("reviewing", start), entry("approved", done)])
    )
    assert info["state"] == "missed"


def test_ret_de_sonuc_sayilir():
    start = NOW - timedelta(hours=10)
    done = NOW - timedelta(hours=1)
    info = build_guarantee_status(
        doc("rejected", [entry("reviewing", start), entry("rejected", done)])
    )
    assert info["state"] == "met"


def test_iptal_edilmis_basvuruda_garanti_gosterilmez():
    info = build_guarantee_status(doc("cancelled", [entry("cancelled", NOW)]))
    assert info["state"] == "closed"


def test_baslangic_kaydi_olmadan_onaylanan_basvuru_pending_kalmaz():
    """Panelden dogrudan onaylanan (reviewing kaydi olmayan) basvuru celiskili gorunmemeli."""
    done = NOW - timedelta(hours=1)
    info = build_guarantee_status(doc("approved", [entry("approved", done)]))
    assert info["state"] == "met"
    assert info["finished_at"] == done.isoformat()


def test_baslangic_ve_gecmis_kaydi_olmadan_onaylanan_basvuru():
    info = build_guarantee_status(doc("approved", []))
    assert info["state"] == "met"


def test_datetime_nesnesi_de_kabul_edilir():
    start = NOW - timedelta(hours=3)
    info = build_guarantee_status({"status": "reviewing", "zami_transferred_at": start})
    assert info["state"] == "running"
