"""Iteration 117: zami_rpa form doldurma adimlarinin birim testleri.

`fill_application` icindeki tek buyuk closure `_FieldSetter` sinifina ve kucuk
adim fonksiyonlarina bolundu. Burada Playwright yerine sahte page/locator
nesneleri kullanilarak her adim ayri ayri dogrulanir (tarayici gerekmez).
"""

import asyncio
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import zami_rpa  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# --------------------------------------------------------------- sahte nesneler
class FakeLocator:
    def __init__(
        self,
        tag="input",
        input_type="text",
        count=1,
        disabled=False,
        visible=True,
        class_name="",
        select_ok_by="label",
    ):
        self.tag = tag
        self.input_type = input_type
        self._count = count
        self._disabled = disabled
        self._visible = visible
        self.class_name = class_name
        self.select_ok_by = select_ok_by
        self.filled_value = None
        self.checked = False
        self.selected = None

    @property
    def first(self):
        return self

    async def count(self):
        return self._count

    async def is_disabled(self):
        return self._disabled

    async def is_visible(self):
        return self._visible

    async def evaluate(self, script, *_args):
        if "tagName" in script:
            return self.tag
        if "el.type" in script:
            return self.input_type
        if "className" in script:
            return self.class_name
        return ""

    async def fill(self, value, timeout=None):
        self.filled_value = value

    async def dispatch_event(self, name):
        return None

    async def select_option(self, label=None, value=None):
        if label is not None:
            if self.select_ok_by != "label":
                raise RuntimeError("label not found")
            self.selected = ("label", label)
            return
        if self.select_ok_by != "value":
            raise RuntimeError("value not found")
        self.selected = ("value", value)

    async def check(self, timeout=None):
        self.checked = True


class FakeRadioItem:
    def __init__(self, group, value, label):
        self.group = group
        self.value = value
        self.label = label

    async def evaluate(self, script, *_args):
        if "el.value" in script:
            return self.value
        return self.label

    async def check(self, timeout=None):
        self.group.checked_value = self.value


class FakeRadioGroup(FakeLocator):
    def __init__(self, options):
        super().__init__(input_type="radio", count=len(options))
        self.options = options
        self.checked_value = None

    def nth(self, index):
        return FakeRadioItem(self, *self.options[index])


class FakePage:
    def __init__(self, locators=None, eval_result=""):
        self.locators = locators or {}
        self.eval_result = eval_result
        self.requested = []

    def locator(self, selector):
        self.requested.append(selector)
        return self.locators.get(selector, FakeLocator(count=0))

    async def evaluate(self, script, *_args):
        return self.eval_result


# --------------------------------------------------------------- on kosullar
class TestPreconditions:
    def test_missing_form_url(self):
        assert "form_url" in zami_rpa._fill_precondition_error({"fields": {"a": "#a"}})

    def test_empty_mapping(self):
        err = zami_rpa._fill_precondition_error({"form_url": "https://x"})
        assert "eşleme" in err

    def test_traveler_fields_only_is_valid(self):
        mapping = {"form_url": "https://x", "traveler_fields": {"first_name": "#p{i}"}}
        assert zami_rpa._fill_precondition_error(mapping) == ""

    def test_fill_application_returns_error_without_browser(self, monkeypatch):
        async def fake_mapping():
            return {"form_url": "", "fields": {}}

        monkeypatch.setattr(zami_rpa, "get_mapping", fake_mapping)
        res = run(zami_rpa.fill_application({}, {"globals": {}}))
        assert res["ok"] is False
        assert "form_url" in res["error"]


# --------------------------------------------------------------- selector sablonu
class TestTravelerSelector:
    def test_zero_based_placeholder(self):
        assert zami_rpa.traveler_selector("pax[{i}][first_name]", 0) == "pax[0][first_name]"
        assert zami_rpa.traveler_selector("pax[{i}][first_name]", 2) == "pax[2][first_name]"

    def test_one_based_placeholder(self):
        assert zami_rpa.traveler_selector("#traveler_{n}_name", 0) == "#traveler_1_name"
        assert zami_rpa.traveler_selector("#traveler_{n}_name", 3) == "#traveler_4_name"

    def test_both_placeholders(self):
        assert zami_rpa.traveler_selector("#p{i}-{n}", 1) == "#p1-2"


# --------------------------------------------------------------- alan doldurucu
class TestFieldSetter:
    def test_text_field_filled(self):
        loc = FakeLocator()
        page = FakePage({"#name": loc})
        setter = zami_rpa._FieldSetter(page)
        assert run(setter.set("#name", "AHMET")) is True
        assert setter.filled == ["#name"]
        assert setter.missing == []
        assert loc.filled_value == "AHMET"
        assert setter.values["#name"] == "AHMET"

    def test_empty_value_skipped_silently(self):
        setter = zami_rpa._FieldSetter(FakePage({"#name": FakeLocator()}))
        assert run(setter.set("#name", "")) is False
        assert run(setter.set("#name", None)) is False
        assert setter.filled == [] and setter.missing == [] and setter.values == {}

    def test_selector_not_found_goes_to_missing(self):
        setter = zami_rpa._FieldSetter(FakePage())
        assert run(setter.set("#yok", "X")) is False
        assert setter.missing == ["#yok"]
        assert setter.skipped_disabled == []

    def test_disabled_field_goes_to_skipped_not_missing(self):
        page = FakePage({"#locked": FakeLocator(disabled=True)})
        setter = zami_rpa._FieldSetter(page)
        assert run(setter.set("#locked", "X")) is False
        assert setter.skipped_disabled == ["#locked"]
        assert setter.missing == []

    def test_hidden_field_goes_to_skipped(self):
        page = FakePage({"#hidden": FakeLocator(visible=False)})
        setter = zami_rpa._FieldSetter(page)
        run(setter.set("#hidden", "X"))
        assert setter.skipped_disabled == ["#hidden"]

    def test_select_prefers_label(self):
        loc = FakeLocator(tag="select", input_type="select-one", select_ok_by="label")
        setter = zami_rpa._FieldSetter(FakePage({"#country": loc}))
        assert run(setter.set("#country", "Turkey")) is True
        assert loc.selected == ("label", "Turkey")

    def test_select_falls_back_to_value(self):
        loc = FakeLocator(tag="select", input_type="select-one", select_ok_by="value")
        setter = zami_rpa._FieldSetter(FakePage({"#country": loc}))
        assert run(setter.set("#country", "TR")) is True
        assert loc.selected == ("value", "TR")

    def test_select_failure_marks_missing(self):
        loc = FakeLocator(tag="select", input_type="select-one", select_ok_by="none")
        setter = zami_rpa._FieldSetter(FakePage({"#country": loc}))
        assert run(setter.set("#country", "XX")) is False
        assert setter.missing == ["#country"]

    def test_checkbox_truthy_checked(self):
        loc = FakeLocator(input_type="checkbox")
        setter = zami_rpa._FieldSetter(FakePage({"#terms": loc}))
        assert run(setter.set("#terms", "evet")) is True
        assert loc.checked is True
        assert setter.filled == ["#terms"]

    def test_checkbox_falsy_not_counted_as_missing(self):
        loc = FakeLocator(input_type="checkbox")
        setter = zami_rpa._FieldSetter(FakePage({"#terms": loc}))
        assert run(setter.set("#terms", "0")) is False
        assert loc.checked is False
        assert setter.missing == [] and setter.filled == []

    def test_radio_matches_by_label(self):
        group = FakeRadioGroup([("M", "Erkek"), ("F", "Kadın")])
        setter = zami_rpa._FieldSetter(FakePage({"input[name=gender]": group}))
        assert run(setter.set("input[name=gender]", "Kadın")) is True
        assert group.checked_value == "F"

    def test_radio_matches_by_value(self):
        group = FakeRadioGroup([("M", "Erkek"), ("F", "Kadın")])
        setter = zami_rpa._FieldSetter(FakePage({"input[name=gender]": group}))
        assert run(setter.set("input[name=gender]", "M")) is True
        assert group.checked_value == "M"

    def test_radio_no_match_marks_missing(self):
        group = FakeRadioGroup([("M", "Erkek")])
        setter = zami_rpa._FieldSetter(FakePage({"input[name=gender]": group}))
        assert run(setter.set("input[name=gender]", "Diger")) is False
        assert setter.missing == ["input[name=gender]"]


class TestRetrySkipped:
    def test_no_skipped_returns_false(self):
        setter = zami_rpa._FieldSetter(FakePage())
        assert run(setter.retry_skipped()) is False

    def test_unlocked_field_is_filled_on_retry(self):
        loc = FakeLocator(disabled=True)
        page = FakePage({"#city": loc})
        setter = zami_rpa._FieldSetter(page)
        run(setter.set("#city", "DUBAI"))
        assert setter.skipped_disabled == ["#city"]

        loc._disabled = False  # portal dogrulamadan sonra alani acti
        assert run(setter.retry_skipped()) is True
        assert setter.filled == ["#city"]
        assert setter.skipped_disabled == []
        assert loc.filled_value == "DUBAI"

    def test_still_locked_field_stays_skipped(self):
        loc = FakeLocator(disabled=True)
        setter = zami_rpa._FieldSetter(FakePage({"#city": loc}))
        run(setter.set("#city", "DUBAI"))
        assert run(setter.retry_skipped()) is True
        assert setter.skipped_disabled == ["#city"]
        assert setter.filled == []


# --------------------------------------------------------------- esleme adimi
class TestFillMappedFields:
    def _page(self):
        return FakePage(
            {
                "#agency": FakeLocator(),
                "#travel_date": FakeLocator(),
                "pax[0][first_name]": FakeLocator(),
                "pax[1][first_name]": FakeLocator(),
                "#pax_1_last": FakeLocator(),
                "#pax_2_last": FakeLocator(),
            }
        )

    def test_constants_globals_and_travelers(self):
        page = self._page()
        setter = zami_rpa._FieldSetter(page)
        mapping = {
            "constants": {"#agency": "DUBAI VIZE HATTI"},
            "fields": {"travel_date": "#travel_date"},
            "traveler_fields": {
                "first_name": "pax[{i}][first_name]",
                "last_name": "#pax_{n}_last",
            },
        }
        payload = {
            "globals": {"travel_date": "2026-07-01"},
            "travelers": [
                {"first_name": "AHMET", "last_name": "YILMAZ"},
                {"first_name": "AYSE", "last_name": "YILMAZ"},
            ],
        }
        run(zami_rpa._fill_mapped_fields(setter, mapping, payload))
        assert setter.filled == [
            "#agency",
            "#travel_date",
            "pax[0][first_name]",
            "#pax_1_last",
            "pax[1][first_name]",
            "#pax_2_last",
        ]
        assert setter.missing == []
        assert page.locators["#agency"].filled_value == "DUBAI VIZE HATTI"
        assert page.locators["pax[1][first_name]"].filled_value == "AYSE"

    def test_missing_global_value_is_not_marked_missing(self):
        page = self._page()
        setter = zami_rpa._FieldSetter(page)
        mapping = {"fields": {"travel_date": "#travel_date"}}
        run(zami_rpa._fill_mapped_fields(setter, mapping, {"globals": {}}))
        assert setter.filled == [] and setter.missing == []

    def test_empty_mapping_is_noop(self):
        setter = zami_rpa._FieldSetter(self._page())
        run(zami_rpa._fill_mapped_fields(setter, {}, {}))
        assert setter.filled == [] and setter.missing == [] and setter.values == {}


# --------------------------------------------------------------- yardimci tiklar
class TestHelperClicks:
    def test_all_helpers_attempted(self, monkeypatch):
        clicked = []

        async def fake_click(page, selectors):
            clicked.append(selectors[0])
            return False

        monkeypatch.setattr(zami_rpa, "_click_first", fake_click)
        run(zami_rpa._run_helper_clicks(FakePage(), {"helper_selectors": ["#tr", "#ar"]}))
        assert clicked == ["#tr", "#ar"]

    def test_click_error_does_not_raise(self, monkeypatch):
        async def boom(page, selectors):
            raise RuntimeError("detached")

        monkeypatch.setattr(zami_rpa, "_click_first", boom)
        run(zami_rpa._run_helper_clicks(FakePage(), {"helper_selectors": ["#tr"]}))

    def test_no_helpers_is_noop(self, monkeypatch):
        async def fake_click(page, selectors):
            pytest.fail("should not click")

        monkeypatch.setattr(zami_rpa, "_click_first", fake_click)
        run(zami_rpa._run_helper_clicks(FakePage(), {}))


# --------------------------------------------------------------- portal dogrulama
class TestPortalValidation:
    def test_no_validate_selector_returns_empty(self):
        setter = zami_rpa._FieldSetter(FakePage())
        assert run(zami_rpa._run_portal_validation(FakePage(), {}, setter)) == ("", "")

    def test_click_failure_returns_empty(self, monkeypatch):
        async def fake_click(page, selectors):
            return False

        monkeypatch.setattr(zami_rpa, "_click_first", fake_click)
        setter = zami_rpa._FieldSetter(FakePage())
        out = run(
            zami_rpa._run_portal_validation(FakePage(), {"validate_selector": "#v"}, setter)
        )
        assert out == ("", "")

    def test_unlocked_field_retried_after_validation(self, monkeypatch):
        loc = FakeLocator(disabled=True)
        page = FakePage({"#city": loc}, eval_result="Zorunlu alan")
        clicks = []

        async def fake_click(_page, selectors):
            clicks.append(selectors[0])
            loc._disabled = False  # dogrulama alani acti
            return True

        async def fake_sleep(_secs):
            return None

        async def fake_shot(_page):
            return "shot.png"

        monkeypatch.setattr(zami_rpa, "_click_first", fake_click)
        monkeypatch.setattr(zami_rpa, "_shot", fake_shot)
        monkeypatch.setattr(zami_rpa.asyncio, "sleep", fake_sleep)

        setter = zami_rpa._FieldSetter(page)
        run(setter.set("#city", "DUBAI"))
        text, shot = run(
            zami_rpa._run_portal_validation(page, {"validate_selector": "#v"}, setter)
        )
        assert clicks == ["#v", "#v"]  # dogrulama iki kez tetiklenir
        assert setter.filled == ["#city"]
        assert text == "Zorunlu alan"
        assert shot == "shot.png"
