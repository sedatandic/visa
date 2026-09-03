"""zami.py saf fonksiyonlarinin refactor oncesi/sonrasi cikti karsilastirmasi.

Kullanim:
    python zami_pure_snapshot.py save   # refactor ONCESI
    python zami_pure_snapshot.py check  # refactor SONRASI
"""

import json
import pathlib
import sys

sys.path.insert(0, "/app/backend")

import zami  # noqa: E402

SNAP = pathlib.Path("/tmp/zami_pure_snapshot.json")

FORM_HTML = """
<form action="/save" id="f1">
  <input type="hidden" name="csrf" value="x">
  <input type="submit" name="go" value="Save">
  <input type="button" name="b" value="B">
  <input type="reset" name="r">
  <input type="image" name="img">
  <label for="fn">First Name</label>
  <input type="text" name="fn" id="fn" placeholder="Ad">
  <label>Last Name <input type="text" name="ln"></label>
  <input type="text" name="pn" aria-label="Passport Number">
  <input type="text" id="onlyid" placeholder="Sadece id">
  <input type="text">
  <input type="date" name="bd" placeholder="Birth Date">
  <input type="email" name="em" placeholder="E-mail Address">
  <input type="tel" name="mp" placeholder="Mobile Phone">
  <input type="checkbox" name="ck" placeholder="Onay">
  <textarea name="vs_cm" placeholder="Remarks / Notes"></textarea>
  <select name="gn">
    <option value="">Gender</option>
    <option value="M">Male</option>
    <option>Female</option>
  </select>
  <select name="ms" id="ms"><option value="s">Marital Status Single</option></select>
  <input type="text" name="pax[0].mother" placeholder="Mother Name">
  <input type="text" name="pax[1].father" placeholder="Father's Name">
  <input type="text" name="pf_tt" placeholder="Profession / Occupation">
  <input type="text" name="ad" placeholder="Arrival Date">
  <input type="text" name="dd" placeholder="Departure Date">
  <input type="text" name="dr_rf" placeholder="Reference No">
  <input type="text" name="bc_tt" placeholder="Birth Country">
  <input type="text" name="nt_tt" placeholder="Nationality">
  <input type="text" name="zzz_unknown" placeholder="Tamamen alakasiz alan">
  <input type="text" name="  " id="">
</form>
"""

CAPTURES = [
    {},
    {"form": {"fields": []}},
    {
        "form": {
            "url": "https://z/form",
            "submit_selector": "button.save",
            "fields": None,
        }
    },
    {
        "form": {"fields": [{"selector": "", "label": "bos"}, {"label": "selectorsuz"}]},
    },
    {
        "form": {
            "url": " https://z/form ",
            "submit_selector": "button.save",
            "fields": [
                {"selector": '[name="fn"]', "label": "First Name", "name": "fn", "type": "text"},
                {"selector": '[name="ln"]', "label": "Last Name", "name": "ln", "type": "text"},
                {"selector": '[name="fn"]', "label": "First Name tekrar", "name": "fn"},
                {"selector": '[name="pn"]', "label": "Passport Number", "name": "pn"},
                {"selector": '[name="ad"]', "label": "Arrival Date", "name": "ad"},
                {"selector": '[name="dr_rf"]', "label": "Reference", "name": "dr_rf"},
                {"selector": '[name="mp"]', "label": "Mobile Phone", "name": "mp"},
                {"selector": '[name="ms"]', "label": "Marital Status", "name": "ms"},
                {"selector": '[name="pf_tt"]', "label": "Profession", "name": "pf_tt"},
                {"selector": '[name="mo"]', "label": "Mother Name", "name": "mo"},
                {"selector": '[name="fa"]', "label": "Father Name", "name": "fa"},
                {"selector": '[name="pax[0].fn"]', "label": "Passenger First Name"},
                {"selector": '[name="pax[1].ln"]', "label": "Passenger Last Name"},
                {"selector": '[name="bc_tt"]', "label": "Birth Country"},
                {"selector": '[name="nt_tt"]', "label": "Nationality"},
                {"selector": '[name="zzz"]', "label": "Alakasiz"},
            ],
        },
        "status": {
            "url": "https://z/status",
            "search_selector": '[name="pn"]',
            "row_selector": "tr.row",
        },
    },
    {
        "form": {"fields": [{"selector": '[name="zzz"]', "label": "Hicbir sey"}]},
        "status": {},
    },
]


def build() -> dict:
    return {
        "parse_form_fields": zami.parse_form_fields(FORM_HTML),
        "parse_form_fields_empty": zami.parse_form_fields(""),
        "parse_form_fields_none": zami.parse_form_fields(None),
        "suggest_mapping": [zami.suggest_mapping(c) for c in CAPTURES],
        "suggest_mapping_none": zami.suggest_mapping(None),
    }


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    data = json.loads(json.dumps(build(), default=str, sort_keys=True))
    if mode == "save":
        SNAP.write_text(json.dumps(data, indent=1, ensure_ascii=False))
        print(f"kaydedildi -> {SNAP}")
        print("parse_form_fields alan sayisi:", len(data["parse_form_fields"]))
        print("suggest_mapping vaka sayisi:", len(data["suggest_mapping"]))
        return

    old = json.loads(SNAP.read_text())
    if old == data:
        print("BIREBIR AYNI: parse_form_fields + suggest_mapping ciktilari degismedi")
        return
    print("!!! FARK VAR")
    for key in old:
        if old[key] != data[key]:
            print("--- FARKLI ANAHTAR:", key)
            print("OLD:", json.dumps(old[key], ensure_ascii=False)[:1400])
            print("NEW:", json.dumps(data[key], ensure_ascii=False)[:1400])
    sys.exit(1)


if __name__ == "__main__":
    main()
