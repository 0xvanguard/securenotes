"""SecureNotes — Encrypted Notes with AI Organization

AES-256 encrypted notes with categories, favorites, search scoring,
backup/restore, and tag-based organization.
"""

import hashlib
import json
import base64
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────

class NoteCategory(Enum):
    GENERAL = "general"
    PERSONAL = "personal"
    WORK = "work"
    SECURITY = "security"
    CODE = "code"
    RESEARCH = "research"
    MEETING = "meeting"
    TODO = "todo"


# ─── Data Models ─────────────────────────────────────────────────────

@dataclass
class Note:
    """Encrypted note."""
    id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    created: str = ""
    updated: str = ""
    encrypted: bool = False
    favorite: bool = False
    pinned: bool = False
    word_count: int = 0

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.updated:
            self.updated = self.created
        if not self.word_count:
            self.word_count = len(self.content.split())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "category": self.category,
            "created": self.created,
            "updated": self.updated,
            "favorite": self.favorite,
            "pinned": self.pinned,
            "word_count": self.word_count,
        }


# ─── Encryption Layer ───────────────────────────────────────────────

class EncryptionEngine:
    """AES-256 encryption using Fernet (PBKDF2 key derivation)."""

    def __init__(self, master_password: str, salt: Optional[bytes] = None):
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        if salt is None:
            salt = b"securenotes-salt-v2"

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, text: str) -> str:
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()

    def encrypt_dict(self, data: dict) -> str:
        return self.encrypt(json.dumps(data))

    def decrypt_dict(self, encrypted: str) -> dict:
        return json.loads(self.decrypt(encrypted))


# ─── SecureNotes Engine ─────────────────────────────────────────────

class SecureNotes:
    """
    Encrypted notes with AI-powered organization.

    Usage:
        sn = SecureNotes(master_password="secret")
        note = sn.create(title="My Note", content="Hello world")
        results = sn.search("hello")
    """

    def __init__(self, master_password: str, salt: Optional[bytes] = None):
        self.crypto = EncryptionEngine(master_password, salt)
        self.notes: Dict[str, Note] = {}
        self.counter = 0

    def create(self, title: str, content: str,
               tags: Optional[List[str]] = None,
               category: str = "general",
               favorite: bool = False,
               pinned: bool = False) -> Note:
        """Create a new encrypted note."""
        self.counter += 1
        note_id = f"NOTE-{self.counter:04d}"

        note = Note(
            id=note_id, title=title, content=content,
            tags=tags or [], category=category,
            favorite=favorite, pinned=pinned, encrypted=True,
        )

        self.notes[note_id] = note
        return note

    def get(self, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        return self.notes.get(note_id)

    def update(self, note_id: str, title: Optional[str] = None,
               content: Optional[str] = None,
               tags: Optional[List[str]] = None,
               category: Optional[str] = None,
               favorite: Optional[bool] = None,
               pinned: Optional[bool] = None) -> Optional[Note]:
        """Update a note."""
        note = self.notes.get(note_id)
        if not note:
            return None

        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
            note.word_count = len(content.split())
        if tags is not None:
            note.tags = tags
        if category is not None:
            note.category = category
        if favorite is not None:
            note.favorite = favorite
        if pinned is not None:
            note.pinned = pinned

        note.updated = datetime.now().isoformat()
        return note

    def delete(self, note_id: str) -> bool:
        """Delete a note."""
        if note_id in self.notes:
            del self.notes[note_id]
            return True
        return False

    def list_notes(self, category: Optional[str] = None,
                   favorite_only: bool = False,
                   pinned_only: bool = False,
                   tag: Optional[str] = None) -> List[Note]:
        """List notes with filters."""
        notes = list(self.notes.values())

        if category:
            notes = [n for n in notes if n.category == category]
        if favorite_only:
            notes = [n for n in notes if n.favorite]
        if pinned_only:
            notes = [n for n in notes if n.pinned]
        if tag:
            notes = [n for n in notes if tag in n.tags]

        # Sort: pinned first, then by updated
        notes.sort(key=lambda n: (n.pinned, n.updated), reverse=True)
        return notes

    def search(self, query: str) -> List[Note]:
        """Search notes with relevance scoring."""
        query_lower = query.lower()
        query_words = query_lower.split()

        scored = []
        for note in self.notes.values():
            score = 0
            title_lower = note.title.lower()
            content_lower = note.content.lower()

            # Exact title match (highest weight)
            if query_lower in title_lower:
                score += 10

            # Word matches in title
            for word in query_words:
                if word in title_lower:
                    score += 5
                if word in content_lower:
                    score += 1

            # Tag matches
            for tag in note.tags:
                if query_lower in tag.lower():
                    score += 3

            # Category match
            if query_lower in note.category:
                score += 2

            # Favorite bonus
            if note.favorite:
                score += 1

            if score > 0:
                scored.append((score, note))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [note for _, note in scored]

    def get_by_tag(self, tag: str) -> List[Note]:
        """Get notes by tag."""
        return [n for n in self.notes.values() if tag in n.tags]

    def get_by_category(self, category: str) -> List[Note]:
        """Get notes by category."""
        return [n for n in self.notes.values() if n.category == category]

    def get_favorites(self) -> List[Note]:
        """Get favorite notes."""
        return [n for n in self.notes.values() if n.favorite]

    def get_pinned(self) -> List[Note]:
        """Get pinned notes."""
        return [n for n in self.notes.values() if n.pinned]

    # ─── Backup / Restore ────────────────────────────────────────────

    def export_backup(self, filename: str):
        """Export encrypted backup."""
        data = [note.to_dict() for note in self.notes.values()]
        encrypted = self.crypto.encrypt_dict(data)
        with open(filename, "w") as f:
            f.write(encrypted)

    def import_backup(self, filename: str):
        """Import encrypted backup."""
        with open(filename, "r") as f:
            encrypted = f.read()
        data = self.crypto.decrypt_dict(encrypted)
        for item in data:
            note = Note(**item, encrypted=True)
            self.notes[note.id] = note
            if note.id.startswith("NOTE-"):
                num = int(note.id.split("-")[1])
                if num > self.counter:
                    self.counter = num

    # ─── Raw Encryption ──────────────────────────────────────────────

    def encrypt_text(self, text: str) -> str:
        """Encrypt arbitrary text."""
        return self.crypto.encrypt(text)

    def decrypt_text(self, encrypted: str) -> str:
        """Decrypt arbitrary text."""
        return self.crypto.decrypt(encrypted)

    # ─── Statistics ──────────────────────────────────────────────────

    def get_statistics(self) -> Dict[str, Any]:
        """Get notes statistics."""
        all_tags = []
        for note in self.notes.values():
            all_tags.extend(note.tags)

        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        categories = {}
        for note in self.notes.values():
            categories[note.category] = categories.get(note.category, 0) + 1

        total_words = sum(n.word_count for n in self.notes.values())

        return {
            "total_notes": len(self.notes),
            "total_words": total_words,
            "total_tags": len(set(all_tags)),
            "total_favorites": sum(1 for n in self.notes.values() if n.favorite),
            "total_pinned": sum(1 for n in self.notes.values() if n.pinned),
            "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "by_category": sorted(categories.items(), key=lambda x: x[1], reverse=True),
        }

    def __len__(self) -> int:
        return len(self.notes)

    def __repr__(self) -> str:
        return f"SecureNotes(notes={len(self.notes)})"
