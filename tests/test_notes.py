"""Tests for SecureNotes"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.notes import SecureNotes, Note, NoteCategory, EncryptionEngine


sn = SecureNotes(master_password="test-password-123")


def test_note_category_enum():
    assert NoteCategory.GENERAL.value == "general"
    assert NoteCategory.SECURITY.value == "security"
    assert NoteCategory.CODE.value == "code"
    assert len(list(NoteCategory)) == 8
    print("✅ NoteCategory enum OK")


def test_note_creation():
    note = sn.create(title="Test Note", content="Hello world")
    assert isinstance(note, Note)
    assert note.id.startswith("NOTE-")
    assert note.title == "Test Note"
    assert note.encrypted is True
    print(f"✅ Note creation: {note.id}")


def test_note_tags():
    note = sn.create(title="Tagged", content="Content", tags=["work", "important"])
    assert note.tags == ["work", "important"]
    print("✅ Note tags OK")


def test_note_category():
    note = sn.create(title="Categorized", content="Content", category="security")
    assert note.category == "security"
    print("✅ Note category OK")


def test_note_favorite():
    note = sn.create(title="Fav", content="Content", favorite=True)
    assert note.favorite is True
    print("✅ Note favorite OK")


def test_note_pinned():
    note = sn.create(title="Pinned", content="Content", pinned=True)
    assert note.pinned is True
    print("✅ Note pinned OK")


def test_note_to_dict():
    note = sn.create(title="Dict Test", content="Content")
    d = note.to_dict()
    assert d["title"] == "Dict Test"
    assert "word_count" in d
    print("✅ Note to_dict OK")


def test_get_note():
    note = sn.create(title="Get Me", content="Content")
    got = sn.get(note.id)
    assert got is not None
    assert got.title == "Get Me"
    print("✅ Get note OK")


def test_get_nonexistent():
    got = sn.get("NOTE-9999")
    assert got is None
    print("✅ Get nonexistent OK")


def test_update_note():
    note = sn.create(title="Original", content="Content")
    updated = sn.update(note.id, title="Updated", content="New content")
    assert updated.title == "Updated"
    assert updated.content == "New content"
    assert updated.word_count == 2
    print("✅ Update note OK")


def test_update_tags():
    note = sn.create(title="Tags", content="Content", tags=["old"])
    updated = sn.update(note.id, tags=["new", "tags"])
    assert updated.tags == ["new", "tags"]
    print("✅ Update tags OK")


def test_update_favorite():
    note = sn.create(title="Fav", content="Content")
    sn.update(note.id, favorite=True)
    assert sn.get(note.id).favorite is True
    print("✅ Update favorite OK")


def test_delete_note():
    note = sn.create(title="Delete Me", content="Content")
    ok = sn.delete(note.id)
    assert ok is True
    assert sn.get(note.id) is None
    print("✅ Delete note OK")


def test_delete_nonexistent():
    ok = sn.delete("NOTE-9999")
    assert ok is False
    print("✅ Delete nonexistent OK")


def test_search():
    note = sn.create(title="Password Manager", content="Use strong passwords")
    results = sn.search("password")
    assert len(results) > 0
    assert any(n.id == note.id for n in results)
    print(f"✅ Search: {len(results)} results")


def test_search_by_tag():
    sn.create(title="Tagged", content="Content", tags=["crypto"])
    results = sn.search("crypto")
    assert len(results) > 0
    print("✅ Search by tag OK")


def test_search_relevance():
    """Title matches should rank higher than content matches."""
    sn.create(title="Encryption Guide", content="General content about security")
    sn.create(title="Security Basics", content="Encryption is important")
    results = sn.search("encryption")
    assert len(results) >= 2
    # First result should have title match
    assert "encryption" in results[0].title.lower()
    print("✅ Search relevance OK")


def test_list_notes():
    sn.create(title="List Test", content="Content", category="work")
    notes = sn.list_notes(category="work")
    assert len(notes) > 0
    assert all(n.category == "work" for n in notes)
    print(f"✅ List notes: {len(notes)} in 'work'")


def test_list_favorites():
    sn.create(title="Fav List", content="Content", favorite=True)
    favs = sn.list_notes(favorite_only=True)
    assert len(favs) > 0
    assert all(n.favorite for n in favs)
    print(f"✅ List favorites: {len(favs)}")


def test_list_pinned():
    sn.create(title="Pinned List", content="Content", pinned=True)
    pinned = sn.list_notes(pinned_only=True)
    assert len(pinned) > 0
    assert all(n.pinned for n in pinned)
    print(f"✅ List pinned: {len(pinned)}")


def test_list_by_tag():
    sn.create(title="Tagged List", content="Content", tags=["urgent"])
    tagged = sn.list_notes(tag="urgent")
    assert len(tagged) > 0
    print(f"✅ List by tag: {len(tagged)}")


def test_get_by_tag():
    sn.create(title="Crypto Note", content="Content", tags=["crypto"])
    results = sn.get_by_tag("crypto")
    assert len(results) > 0
    print("✅ Get by tag OK")


def test_get_by_category():
    sn.create(title="Code Note", content="Content", category="code")
    results = sn.get_by_category("code")
    assert len(results) > 0
    print("✅ Get by category OK")


def test_get_favorites():
    sn.create(title="Fav Get", content="Content", favorite=True)
    favs = sn.get_favorites()
    assert len(favs) > 0
    print("✅ Get favorites OK")


def test_get_pinned():
    sn.create(title="Pinned Get", content="Content", pinned=True)
    pinned = sn.get_pinned()
    assert len(pinned) > 0
    print("✅ Get pinned OK")


def test_encrypt_decrypt():
    original = "Hello, this is a secret message!"
    encrypted = sn.encrypt_text(original)
    assert encrypted != original
    decrypted = sn.decrypt_text(encrypted)
    assert decrypted == original
    print("✅ Encrypt/decrypt OK")


def test_backup_restore():
    sn.create(title="Backup Test", content="Important data")
    with tempfile.NamedTemporaryFile(suffix=".enc", delete=False) as f:
        path = f.name
    try:
        sn.export_backup(path)
        sn2 = SecureNotes(master_password="test-password-123")
        sn2.import_backup(path)
        assert len(sn2) > 0
    finally:
        os.unlink(path)
    print("✅ Backup/restore OK")


def test_statistics():
    stats = sn.get_statistics()
    assert "total_notes" in stats
    assert "total_words" in stats
    assert "top_tags" in stats
    assert stats["total_notes"] > 0
    print(f"✅ Statistics: {stats['total_notes']} notes, {stats['total_words']} words")


def test_len():
    initial = len(sn)
    sn.create(title="Len Test", content="Content")
    assert len(sn) == initial + 1
    print(f"✅ Len: {len(sn)} notes")


def test_note_word_count():
    note = sn.create(title="Words", content="one two three four five")
    assert note.word_count == 5
    print("✅ Word count OK")


if __name__ == "__main__":
    test_note_category_enum()
    test_note_creation()
    test_note_tags()
    test_note_category()
    test_note_favorite()
    test_note_pinned()
    test_note_to_dict()
    test_get_note()
    test_get_nonexistent()
    test_update_note()
    test_update_tags()
    test_update_favorite()
    test_delete_note()
    test_delete_nonexistent()
    test_search()
    test_search_by_tag()
    test_search_relevance()
    test_list_notes()
    test_list_favorites()
    test_list_pinned()
    test_list_by_tag()
    test_get_by_tag()
    test_get_by_category()
    test_get_favorites()
    test_get_pinned()
    test_encrypt_decrypt()
    test_backup_restore()
    test_statistics()
    test_len()
    test_note_word_count()
    print("\n🎉 All 30 tests passed!")
