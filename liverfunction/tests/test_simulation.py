import pytest
from liverfunction.tests import data
from liverfunction import simulation as lfsim


def test_load_model():
    r = lfsim.load_model(model_path=data.APAP_SBML)
    assert r is not None


def test_get_doses_keys():
    r = lfsim.load_model(model_path=data.APAP_SBML)
    keys = lfsim.get_doses_keys(r)

    assert len(keys) == 10
    assert "IVDOSE_apap" in keys
    assert "PODOSE_apap" in keys
    for key in keys:
        assert key.startswith("PODOSE_") or key.startswith("IVDOSE_")
