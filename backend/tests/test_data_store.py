"""Unit tests for DataStore indexing and entity graph resolution."""

import pytest
from app.core.models import EntityType
from app.data.store import DataStore


def test_datastore_indexing():
    """Verify in-memory data store indexes merchants, transactions, and entities correctly."""
    ds = DataStore(auto_seed=True)

    all_merchants = ds.get_all_merchants()
    assert len(all_merchants) == 240

    m1 = ds.get_merchant("M-1001")
    assert m1 is not None
    assert m1.id == "M-1001"

    txns = ds.get_merchant_transactions("M-1001")
    assert len(txns) > 0

    settlements = ds.get_merchant_settlements("M-1001")
    assert isinstance(settlements, list)


def test_shared_identifiers_resolution():
    """Verify reverse indexing of shared entities across merchants."""
    ds = DataStore(auto_seed=True)

    # Ring Alpha shared device check
    shared_dev_merchants = ds.get_shared_merchants_by_entity(EntityType.DEVICE, "DEV-FARM-991")
    assert len(shared_dev_merchants) == 5

    # Check merchant shared identifier summary
    shared_info = ds.get_merchant_shared_identifiers("M-ALPHA-01")
    assert shared_info["total_co_linked_merchants"] >= 4
    assert shared_info["phone"]["id"] == "PH-VOIP-ALPHA"
    assert len(shared_info["phone"]["shared_with"]) == 9  # Shared with 9 other Alpha merchants
