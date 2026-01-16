"""
Session Manager - Unified session storage with persistence.

Handles all research session types (Product, Sovereign, Legacy, Unified)
with file-based persistence to prevent data loss on server restart.
"""
import json
import uuid
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from src.models.unified_session import UnifiedSession, create_thematic_session, create_tot_session, create_unified_session


class SessionManager:
    """
    Unified session manager with persistence.

    Features:
    - Single namespace for all session types
    - File-based persistence (data/sessions/*.json)
    - Automatic session loading on startup
    - Runtime component attachment (GraphManager, ToTManager, etc.)
    """

    def __init__(self, sessions_dir: str = "data/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # In-memory session storage
        self.sessions: Dict[str, UnifiedSession] = {}

        # Load existing sessions from disk
        self._load_sessions_from_disk()

    def _load_sessions_from_disk(self):
        """Load all sessions from disk on startup."""
        session_files = list(self.sessions_dir.glob("*.json"))

        loaded = 0
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = UnifiedSession.from_dict(data)
                    self.sessions[session.metadata.session_id] = session
                    loaded += 1
            except Exception as e:
                print(f"Failed to load session {session_file}: {e}")

        if loaded > 0:
            print(f"✓ Loaded {loaded} existing sessions from disk")

    def _save_session_to_disk(self, session: UnifiedSession):
        """Persist session to disk."""
        session_file = self.sessions_dir / f"{session.metadata.session_id}.json"

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save session {session.metadata.session_id}: {e}")

    def create_session(
        self,
        mode: str,
        title: str,
        goal: str,
        description: str = "",
        axioms: List[str] = None,
        research_type: str = "product",
        session_id: Optional[str] = None
    ) -> UnifiedSession:
        """
        Create a new session in specified mode.

        Args:
            mode: "thematic" | "tot" | "unified"
            title: Session title
            goal: Research goal/question
            description: Detailed description (for thematic mode)
            axioms: Active axiom IDs (for tot/unified modes)
            research_type: Type of research (for thematic mode)
            session_id: Optional custom session ID (generates UUID if None)

        Returns:
            UnifiedSession instance
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Create session based on mode
        if mode == "thematic":
            session = create_thematic_session(session_id, title, goal, description, research_type)
        elif mode == "tot":
            session = create_tot_session(session_id, title, goal, axioms)
        elif mode == "unified":
            session = create_unified_session(session_id, title, goal, description, axioms, research_type)
        else:
            raise ValueError(f"Unknown mode: {mode}. Must be 'thematic', 'tot', or 'unified'")

        # Store in memory
        self.sessions[session_id] = session

        # Persist to disk
        self._save_session_to_disk(session)

        return session

    def get_session(self, session_id: str) -> Optional[UnifiedSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def update_session(self, session: UnifiedSession):
        """Update session and persist changes."""
        session.update_timestamp()
        self.sessions[session.metadata.session_id] = session
        self._save_session_to_disk(session)

    def delete_session(self, session_id: str) -> bool:
        """Delete session from memory and disk."""
        if session_id not in self.sessions:
            return False

        # Remove from memory
        del self.sessions[session_id]

        # Remove from disk
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()

        return True

    def list_sessions(self, mode: Optional[str] = None) -> List[Dict]:
        """
        List all sessions (optionally filtered by mode).

        Returns minimal session info for display.
        """
        sessions_list = []

        for session in self.sessions.values():
            # Filter by mode if specified
            if mode and session.metadata.mode != mode:
                continue

            sessions_list.append(session.export_for_frontend())

        # Sort by created_at (newest first)
        sessions_list.sort(key=lambda s: s['created_at'], reverse=True)

        return sessions_list

    def attach_components(
        self,
        session_id: str,
        graph_manager=None,
        tot_manager=None,
        axiom_manager=None,
        mcts_engine=None,
        orchestrator=None
    ):
        """
        Attach runtime components to session.

        These components are NOT persisted to disk.
        Must be re-attached after loading from disk.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if graph_manager:
            session._graph_manager = graph_manager
        if tot_manager:
            session._tot_manager = tot_manager
        if axiom_manager:
            session._axiom_manager = axiom_manager
        if mcts_engine:
            session._mcts_engine = mcts_engine
        if orchestrator:
            session._orchestrator = orchestrator

    def get_component(self, session_id: str, component_name: str):
        """Get runtime component from session."""
        session = self.get_session(session_id)
        if not session:
            return None

        return getattr(session, f"_{component_name}", None)

    def export_session(self, session_id: str, export_path: Optional[str] = None) -> str:
        """
        Export session as JSON file.

        Args:
            session_id: Session to export
            export_path: Optional custom export path (defaults to data/exports/)

        Returns:
            Path to exported file
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if export_path is None:
            export_dir = Path("data/exports")
            export_dir.mkdir(parents=True, exist_ok=True)
            export_path = export_dir / f"{session_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        export_path = Path(export_path)

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2)

        return str(export_path)

    def import_session(self, import_path: str) -> UnifiedSession:
        """
        Import session from JSON file.

        Args:
            import_path: Path to JSON file

        Returns:
            Imported UnifiedSession
        """
        import_path = Path(import_path)

        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")

        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        session = UnifiedSession.from_dict(data)

        # Store in memory and persist
        self.sessions[session.metadata.session_id] = session
        self._save_session_to_disk(session)

        return session

    def cleanup_old_sessions(self, days: int = 30):
        """Delete sessions older than specified days."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = 0

        for session_id, session in list(self.sessions.items()):
            created = datetime.fromisoformat(session.metadata.created_at)
            if created < cutoff:
                self.delete_session(session_id)
                deleted += 1

        return deleted

    def get_stats(self) -> Dict:
        """Get session statistics."""
        total = len(self.sessions)
        by_mode = {}
        by_status = {}

        for session in self.sessions.values():
            mode = session.metadata.mode
            status = session.metadata.status

            by_mode[mode] = by_mode.get(mode, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_sessions": total,
            "by_mode": by_mode,
            "by_status": by_status,
            "storage_path": str(self.sessions_dir)
        }
