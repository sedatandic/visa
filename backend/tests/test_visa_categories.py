"""Tests for visa categories/tabs restructure (iteration_71)."""
import os
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://otp-admin-flow.preview.emergentagent.com').rstrip('/')


def test_visa_categories_three_with_new_labels():
    r = requests.get(f"{BASE_URL}/api/content/site", timeout=15)
    assert r.status_code == 200
    cats = r.json().get('visa_categories')
    assert isinstance(cats, list)
    assert len(cats) == 3
    ids = [c['id'] for c in cats]
    labels = {c['id']: c['label'] for c in cats}
    assert ids == ['single', 'multiple', 'child']
    assert labels['single'] == 'Tek Girişli Vize'
    assert labels['multiple'] == 'Çok Girişli Vize'
    assert labels['child'] == 'Çocuk Vizesi'
    # ensure no 'other' remains
    assert 'other' not in ids


def test_visa_types_categories_and_auto_suggest():
    r = requests.get(f"{BASE_URL}/api/visa-types", timeout=15)
    assert r.status_code == 200
    data = r.json()
    by_id = {v['id']: v for v in data}
    # extension belongs to single with auto_suggest false (transit visa retired)
    for vid in ['visa_extension_30']:
        assert vid in by_id, f"{vid} missing"
        assert by_id[vid]['category'] == 'single', f"{vid} category {by_id[vid]['category']}"
        assert by_id[vid].get('auto_suggest') is False, f"{vid} auto_suggest not False"
    # the other six should be auto_suggest True
    others = ['visa_30_single', 'visa_60_single', 'visa_30_multi', 'visa_60_multi', 'visa_30_child', 'visa_60_child']
    for vid in others:
        assert vid in by_id
        assert by_id[vid].get('auto_suggest') is True, f"{vid} auto_suggest should be True"


def test_single_category_has_three_visas():
    r = requests.get(f"{BASE_URL}/api/visa-types", timeout=15)
    data = r.json()
    single = [v for v in data if v.get('category') == 'single']
    assert len(single) == 3
    ids = sorted([v['id'] for v in single])
    assert ids == sorted(['visa_30_single', 'visa_60_single', 'visa_extension_30'])
