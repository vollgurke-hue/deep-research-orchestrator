"""
Unit tests for SPODatabase (Cluster 1)
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.core.spo_database import SPODatabase
from src.models.unified_session import SPOTriplet, SPOProvenance


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_spo.db"

    db = SPODatabase(str(db_path))

    yield db

    # Cleanup
    db.close()
    shutil.rmtree(temp_dir)


def test_insert_and_get(temp_db):
    """Test basic insert and retrieval."""
    # Create triplet
    triplet = SPOTriplet(
        id="test_001",
        subject="Solaranlage",
        predicate="ROI-Periode",
        object="15-20 Jahre",
        confidence=0.85,
        tier="bronze",
        provenance=SPOProvenance(
            source_id="response_123",
            extraction_method="llm_structured"
        )
    )

    # Insert
    triplet_id = temp_db.insert(triplet)
    assert triplet_id == "test_001"

    # Retrieve
    retrieved = temp_db.get_by_id(triplet_id)
    assert retrieved is not None
    assert retrieved.subject == "Solaranlage"
    assert retrieved.predicate == "ROI-Periode"
    assert retrieved.object == "15-20 Jahre"
    assert retrieved.confidence == 0.85
    assert retrieved.tier == "bronze"


def test_query_by_subject(temp_db):
    """Test querying by subject."""
    # Insert multiple triplets
    triplets = [
        SPOTriplet(
            id=f"test_{i}",
            subject="Solaranlage",
            predicate=f"prop_{i}",
            object=f"value_{i}",
            confidence=0.8,
            provenance=SPOProvenance("test", "manual")
        )
        for i in range(3)
    ]

    for t in triplets:
        temp_db.insert(t)

    # Query by subject
    results = temp_db.query(subject="Solaranlage")
    assert len(results) == 3
    assert all(r.subject == "Solaranlage" for r in results)


def test_query_by_tier(temp_db):
    """Test querying by tier."""
    # Insert with different tiers
    temp_db.insert(SPOTriplet(
        id="bronze_1",
        subject="A",
        predicate="is",
        object="B",
        confidence=0.5,
        tier="bronze",
        provenance=SPOProvenance("test", "manual")
    ))

    temp_db.insert(SPOTriplet(
        id="silver_1",
        subject="C",
        predicate="is",
        object="D",
        confidence=0.8,
        tier="silver",
        provenance=SPOProvenance("test", "manual")
    ))

    # Query silver only
    results = temp_db.query(tier="silver")
    assert len(results) == 1
    assert results[0].tier == "silver"


def test_promote_tier(temp_db):
    """Test tier promotion."""
    # Insert bronze triplet
    triplet_id = temp_db.insert(SPOTriplet(
        id="promote_test",
        subject="X",
        predicate="Y",
        object="Z",
        confidence=0.9,
        tier="bronze",
        provenance=SPOProvenance("test", "manual")
    ))

    # Promote to silver
    success = temp_db.promote(triplet_id, "silver")
    assert success

    # Verify promotion
    retrieved = temp_db.get_by_id(triplet_id)
    assert retrieved.tier == "silver"


def test_update_provenance(temp_db):
    """Test provenance verification update."""
    # Insert triplet
    triplet_id = temp_db.insert(SPOTriplet(
        id="verify_test",
        subject="A",
        predicate="B",
        object="C",
        confidence=0.7,
        provenance=SPOProvenance("source_1", "llm")
    ))

    # Mark as verified
    success = temp_db.update_provenance(
        triplet_id,
        verified=True,
        verification_source="source_2"
    )
    assert success

    # Verify update
    retrieved = temp_db.get_by_id(triplet_id)
    assert retrieved.provenance.verified is True
    assert retrieved.provenance.verification_count == 1
    assert "source_2" in retrieved.provenance.verification_sources


def test_full_text_search(temp_db):
    """Test FTS5 full-text search."""
    # Insert triplets
    temp_db.insert(SPOTriplet(
        id="search_1",
        subject="Solaranlage Installation",
        predicate="Kosten",
        object="20000 EUR",
        confidence=0.8,
        provenance=SPOProvenance("test", "manual")
    ))

    temp_db.insert(SPOTriplet(
        id="search_2",
        subject="Windkraft",
        predicate="Kosten",
        object="50000 EUR",
        confidence=0.8,
        provenance=SPOProvenance("test", "manual")
    ))

    # Search for "Solaranlage"
    results = temp_db.search("Solaranlage")
    assert len(results) >= 1
    assert any("Solaranlage" in r.subject for r in results)


def test_get_stats(temp_db):
    """Test database statistics."""
    # Insert triplets with different tiers
    for i in range(10):
        temp_db.insert(SPOTriplet(
            id=f"stats_{i}",
            subject=f"S{i}",
            predicate="P",
            object=f"O{i}",
            confidence=0.5 + (i * 0.05),
            tier="bronze" if i < 7 else "silver",
            provenance=SPOProvenance("test", "manual")
        ))

    # Get stats
    stats = temp_db.get_stats()
    assert stats["total_triplets"] == 10
    assert stats["by_tier"]["bronze"] == 7
    assert stats["by_tier"]["silver"] == 3
    assert 0.5 <= stats["avg_confidence"] <= 1.0


def test_delete(temp_db):
    """Test triplet deletion."""
    # Insert triplet
    triplet_id = temp_db.insert(SPOTriplet(
        id="delete_test",
        subject="A",
        predicate="B",
        object="C",
        confidence=0.5,
        provenance=SPOProvenance("test", "manual")
    ))

    # Delete
    success = temp_db.delete(triplet_id)
    assert success

    # Verify deletion
    retrieved = temp_db.get_by_id(triplet_id)
    assert retrieved is None


def test_confidence_validation(temp_db):
    """Test confidence range validation."""
    # Invalid confidence > 1.0
    with pytest.raises(ValueError):
        temp_db.insert(SPOTriplet(
            id="invalid_1",
            subject="A",
            predicate="B",
            object="C",
            confidence=1.5,  # Invalid
            provenance=SPOProvenance("test", "manual")
        ))

    # Invalid confidence < 0.0
    with pytest.raises(ValueError):
        temp_db.insert(SPOTriplet(
            id="invalid_2",
            subject="A",
            predicate="B",
            object="C",
            confidence=-0.5,  # Invalid
            provenance=SPOProvenance("test", "manual")
        ))
