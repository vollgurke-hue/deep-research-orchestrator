"""
SPO Database - SQLite backend for Subject-Predicate-Object tripletts.

Part of Cluster 1: Foundations (SRO Implementation)
Implements Tiered RAG (Bronze/Silver/Gold) storage for structured knowledge.

Design Decision (Gemini Review):
- SQLite over Neo4j for portability and performance
- JSON fields for flexible metadata
- FTS5 for full-text search
"""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models.unified_session import SPOTriplet, SPOProvenance


class SPODatabase:
    """
    SQLite backend for SPO Knowledge Graph.

    Features:
    - CRUD operations for SPO tripletts
    - Tiered RAG (Bronze/Silver/Gold)
    - Provenance tracking
    - Full-text search (FTS5)
    - Efficient queries with indexes

    Usage:
        db = SPODatabase("data/sessions/session_123/spo_graph.db")

        # Insert triplet
        triplet_id = db.insert(triplet)

        # Query by subject
        triplets = db.query(subject="Solaranlage")

        # Promote to higher tier
        db.promote(triplet_id, "silver")
    """

    def __init__(self, db_path: str):
        """
        Initialize SPO Database.

        Args:
            db_path: Path to SQLite database file (will be created if doesn't exist)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name

        self._create_schema()

    def _create_schema(self):
        """Create database schema if not exists."""
        cursor = self.conn.cursor()

        # Main SPO tripletts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spo_triplets (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0),
                tier TEXT CHECK(tier IN ('bronze', 'silver', 'gold')) DEFAULT 'bronze',
                created_at TEXT NOT NULL,
                updated_at TEXT,

                -- Provenance (JSON)
                provenance_json TEXT NOT NULL,

                -- Metadata (JSON)
                metadata_json TEXT
            )
        """)

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subject ON spo_triplets(subject)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predicate ON spo_triplets(predicate)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_object ON spo_triplets(object)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tier ON spo_triplets(tier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON spo_triplets(confidence DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON spo_triplets(created_at DESC)")

        # Full-Text-Search (FTS5) for semantic queries
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS spo_fts USING fts5(
                id UNINDEXED,
                subject,
                predicate,
                object,
                content=spo_triplets,
                content_rowid=rowid
            )
        """)

        # Triggers to keep FTS in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS spo_ai AFTER INSERT ON spo_triplets BEGIN
                INSERT INTO spo_fts(id, subject, predicate, object)
                VALUES (new.id, new.subject, new.predicate, new.object);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS spo_ad AFTER DELETE ON spo_triplets BEGIN
                DELETE FROM spo_fts WHERE id = old.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS spo_au AFTER UPDATE ON spo_triplets BEGIN
                UPDATE spo_fts
                SET subject = new.subject, predicate = new.predicate, object = new.object
                WHERE id = new.id;
            END
        """)

        self.conn.commit()

    def insert(self, triplet: SPOTriplet) -> str:
        """
        Insert new SPO triplet into database.

        Args:
            triplet: SPOTriplet instance

        Returns:
            Triplet ID

        Raises:
            ValueError: If confidence not in range [0, 1]
            sqlite3.IntegrityError: If triplet ID already exists
        """
        # Validate confidence
        if not 0.0 <= triplet.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {triplet.confidence}")

        # Generate ID if not provided
        if not triplet.id:
            triplet.id = f"spo_{uuid.uuid4().hex[:12]}"

        # Set timestamps
        now = datetime.utcnow().isoformat()
        if not triplet.created_at:
            triplet.created_at = now
        triplet.updated_at = now

        # Serialize provenance and metadata to JSON
        provenance_json = json.dumps({
            "source_id": triplet.provenance.source_id,
            "extraction_method": triplet.provenance.extraction_method,
            "model_used": triplet.provenance.model_used,
            "extracted_at": triplet.provenance.extracted_at or now,
            "verified": triplet.provenance.verified,
            "verification_count": triplet.provenance.verification_count,
            "verification_sources": triplet.provenance.verification_sources
        })

        metadata_json = json.dumps(triplet.metadata) if triplet.metadata else "{}"

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO spo_triplets
            (id, subject, predicate, object, confidence, tier, created_at, updated_at, provenance_json, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            triplet.id,
            triplet.subject,
            triplet.predicate,
            triplet.object,
            triplet.confidence,
            triplet.tier,
            triplet.created_at,
            triplet.updated_at,
            provenance_json,
            metadata_json
        ))

        self.conn.commit()
        return triplet.id

    def get_by_id(self, triplet_id: str) -> Optional[SPOTriplet]:
        """
        Get triplet by ID.

        Args:
            triplet_id: Triplet identifier

        Returns:
            SPOTriplet instance or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM spo_triplets WHERE id = ?", (triplet_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_triplet(row)

    def query(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object: Optional[str] = None,
        tier: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[SPOTriplet]:
        """
        Query tripletts with filters.

        Args:
            subject: Filter by subject (exact match)
            predicate: Filter by predicate (exact match)
            object: Filter by object (exact match)
            tier: Filter by tier (bronze|silver|gold)
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return

        Returns:
            List of SPOTriplet instances
        """
        conditions = []
        params = []

        if subject:
            conditions.append("subject = ?")
            params.append(subject)

        if predicate:
            conditions.append("predicate = ?")
            params.append(predicate)

        if object:
            conditions.append("object = ?")
            params.append(object)

        if tier:
            conditions.append("tier = ?")
            params.append(tier)

        if min_confidence > 0.0:
            conditions.append("confidence >= ?")
            params.append(min_confidence)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT * FROM spo_triplets
            WHERE {where_clause}
            ORDER BY confidence DESC, created_at DESC
            LIMIT ?
        """, params)

        return [self._row_to_triplet(row) for row in cursor.fetchall()]

    def search(self, query_text: str, limit: int = 50) -> List[SPOTriplet]:
        """
        Full-text search across subject, predicate, object.

        Args:
            query_text: Search query
            limit: Maximum results

        Returns:
            List of SPOTriplet instances ranked by relevance
        """
        cursor = self.conn.cursor()

        # FTS5 search
        cursor.execute("""
            SELECT t.* FROM spo_triplets t
            JOIN spo_fts f ON t.id = f.id
            WHERE spo_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query_text, limit))

        return [self._row_to_triplet(row) for row in cursor.fetchall()]

    def promote(self, triplet_id: str, new_tier: str) -> bool:
        """
        Promote triplet to higher tier (Bronze → Silver → Gold).

        Args:
            triplet_id: Triplet to promote
            new_tier: New tier (silver | gold)

        Returns:
            True if promoted, False if not found

        Raises:
            ValueError: If new_tier invalid
        """
        if new_tier not in ["bronze", "silver", "gold"]:
            raise ValueError(f"Invalid tier: {new_tier}. Must be bronze|silver|gold")

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE spo_triplets
            SET tier = ?, updated_at = ?
            WHERE id = ?
        """, (new_tier, datetime.utcnow().isoformat(), triplet_id))

        self.conn.commit()
        return cursor.rowcount > 0

    def update_provenance(
        self,
        triplet_id: str,
        verified: bool = True,
        verification_source: Optional[str] = None
    ) -> bool:
        """
        Update verification status in provenance.

        Args:
            triplet_id: Triplet to update
            verified: Mark as verified
            verification_source: Source that verified this (optional)

        Returns:
            True if updated, False if not found
        """
        # Get current provenance
        triplet = self.get_by_id(triplet_id)
        if not triplet:
            return False

        # Update verification
        triplet.provenance.verified = verified
        if verification_source:
            if verification_source not in triplet.provenance.verification_sources:
                triplet.provenance.verification_sources.append(verification_source)
                triplet.provenance.verification_count = len(triplet.provenance.verification_sources)

        # Serialize updated provenance
        provenance_json = json.dumps({
            "source_id": triplet.provenance.source_id,
            "extraction_method": triplet.provenance.extraction_method,
            "model_used": triplet.provenance.model_used,
            "extracted_at": triplet.provenance.extracted_at,
            "verified": triplet.provenance.verified,
            "verification_count": triplet.provenance.verification_count,
            "verification_sources": triplet.provenance.verification_sources
        })

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE spo_triplets
            SET provenance_json = ?, updated_at = ?
            WHERE id = ?
        """, (provenance_json, datetime.utcnow().isoformat(), triplet_id))

        self.conn.commit()
        return cursor.rowcount > 0

    def update_tier(
        self,
        triplet_id: str,
        new_tier: str
    ) -> bool:
        """
        Update triplet tier (for promotion).

        Args:
            triplet_id: Triplet to update
            new_tier: New tier (bronze/silver/gold)

        Returns:
            True if updated, False if not found
        """
        if new_tier not in ["bronze", "silver", "gold"]:
            raise ValueError(f"Invalid tier: {new_tier}")

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE spo_triplets
            SET tier = ?, updated_at = ?
            WHERE id = ?
        """, (new_tier, datetime.utcnow().isoformat(), triplet_id))

        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, triplet_id: str) -> bool:
        """
        Delete triplet by ID.

        Args:
            triplet_id: Triplet to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM spo_triplets WHERE id = ?", (triplet_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            {
                "total_triplets": 42,
                "by_tier": {"bronze": 30, "silver": 10, "gold": 2},
                "verified_count": 12,
                "avg_confidence": 0.75
            }
        """
        cursor = self.conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) as total FROM spo_triplets")
        total = cursor.fetchone()["total"]

        # By tier
        cursor.execute("""
            SELECT tier, COUNT(*) as count
            FROM spo_triplets
            GROUP BY tier
        """)
        by_tier = {row["tier"]: row["count"] for row in cursor.fetchall()}

        # Verified count (from provenance JSON)
        cursor.execute("""
            SELECT COUNT(*) as verified
            FROM spo_triplets
            WHERE json_extract(provenance_json, '$.verified') = 1
        """)
        verified = cursor.fetchone()["verified"]

        # Average confidence
        cursor.execute("SELECT AVG(confidence) as avg_conf FROM spo_triplets")
        avg_conf = cursor.fetchone()["avg_conf"] or 0.0

        return {
            "total_triplets": total,
            "by_tier": by_tier,
            "verified_count": verified,
            "avg_confidence": round(avg_conf, 3)
        }

    def _row_to_triplet(self, row: sqlite3.Row) -> SPOTriplet:
        """Convert database row to SPOTriplet instance."""
        # Parse JSON fields
        provenance_data = json.loads(row["provenance_json"])
        metadata_data = json.loads(row["metadata_json"]) if row["metadata_json"] else {}

        # Reconstruct provenance
        provenance = SPOProvenance(
            source_id=provenance_data["source_id"],
            extraction_method=provenance_data["extraction_method"],
            model_used=provenance_data.get("model_used"),
            extracted_at=provenance_data.get("extracted_at"),
            verified=provenance_data.get("verified", False),
            verification_count=provenance_data.get("verification_count", 0),
            verification_sources=provenance_data.get("verification_sources", [])
        )

        return SPOTriplet(
            id=row["id"],
            subject=row["subject"],
            predicate=row["predicate"],
            object=row["object"],
            confidence=row["confidence"],
            tier=row["tier"],
            provenance=provenance,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            metadata=metadata_data
        )

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
