#!/usr/bin/env python3
"""
SecureNotes CLI — Encrypted notes from the command line.

Usage:
    python cli.py create --title "My Note" --content "Hello world" --tags work,important
    python cli.py list
    python cli.py list --category security
    python cli.py list --favorites
    python cli.py get NOTE-0001
    python cli.py search "password"
    python cli.py update NOTE-0001 --content "Updated"
    python cli.py delete NOTE-0001
    python cli.py stats
    python cli.py encrypt "secret text"
    python cli.py backup --output backup.enc
    python cli.py restore --input backup.enc
"""

import argparse
import getpass
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from notes import SecureNotes, NoteCategory


def get_notes():
    """Get or create SecureNotes instance."""
    password = os.environ.get("SECURENOTES_PASSWORD")
    if not password:
        password = getpass.getpass("Master password: ")
    return SecureNotes(master_password=password)


def cmd_create(args):
    """Create a new note."""
    sn = get_notes()
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    note = sn.create(
        title=args.title, content=args.content,
        tags=tags, category=args.category,
        favorite=args.favorite, pinned=args.pinned,
    )

    print(f"\n📝 Note Created\n{'='*40}")
    print(f"  ID:       {note.id}")
    print(f"  Title:    {note.title}")
    print(f"  Category: {note.category}")
    print(f"  Tags:     {', '.join(note.tags) if note.tags else 'none'}")
    print(f"  Words:    {note.word_count}")
    print(f"  Encrypted:{' ✅' if note.encrypted else ' ❌'}")


def cmd_list(args):
    """List notes."""
    sn = get_notes()

    notes = sn.list_notes(
        category=args.category,
        favorite_only=args.favorites,
        pinned_only=args.pinned,
        tag=args.tag,
    )

    if args.category:
        label = args.category
    elif args.favorites:
        label = "favorites"
    elif args.pinned:
        label = "pinned"
    elif args.tag:
        label = f"tag:{args.tag}"
    else:
        label = "all"

    print(f"\n📋 Notes ({label}) — {len(notes)}\n{'='*60}")
    print(f"{'ID':<12} {'Title':<25} {'Category':<12} {'Words':<8} {'Tags'}")
    print("-" * 70)

    for note in notes:
        pin = "📌" if note.pinned else " "
        fav = "⭐" if note.favorite else " "
        tags = ", ".join(note.tags[:3]) if note.tags else ""
        title = note.title[:22] + "..." if len(note.title) > 25 else note.title
        print(f"{note.id:<12} {pin}{fav} {title:<23} {note.category:<12} {note.word_count:<8} {tags}")


def cmd_get(args):
    """Get a note."""
    sn = get_notes()
    note = sn.get(args.id)

    if not note:
        print(f"\n❌ Note not found: {args.id}")
        return

    pin = "📌 " if note.pinned else ""
    fav = "⭐ " if note.favorite else ""

    print(f"\n{pin}{fav}📝 {note.title}\n{'='*60}")
    print(f"  ID:       {note.id}")
    print(f"  Category: {note.category}")
    print(f"  Tags:     {', '.join(note.tags) if note.tags else 'none'}")
    print(f"  Words:    {note.word_count}")
    print(f"  Created:  {note.created[:19]}")
    print(f"  Updated:  {note.updated[:19]}")
    print(f"\n{'-'*60}")
    print(note.content)
    print(f"{'-'*60}")


def cmd_search(args):
    """Search notes."""
    sn = get_notes()
    results = sn.search(args.query)

    print(f"\n🔍 Search: '{args.query}' — {len(results)} results\n{'='*60}")

    for note in results:
        pin = "📌" if note.pinned else " "
        fav = "⭐" if note.favorite else " "
        print(f"  {note.id} {pin}{fav} {note.title}")
        # Show snippet
        content_lower = note.content.lower()
        idx = content_lower.find(args.query.lower())
        if idx >= 0:
            start = max(0, idx - 30)
            end = min(len(note.content), idx + len(args.query) + 30)
            snippet = note.content[start:end]
            print(f"         ...{snippet}...")
        print()


def cmd_update(args):
    """Update a note."""
    sn = get_notes()

    kwargs = {}
    if args.title:
        kwargs["title"] = args.title
    if args.content:
        kwargs["content"] = args.content
    if args.tags:
        kwargs["tags"] = [t.strip() for t in args.tags.split(",")]
    if args.category:
        kwargs["category"] = args.category
    if args.favorite is not None:
        kwargs["favorite"] = args.favorite
    if args.pinned is not None:
        kwargs["pinned"] = args.pinned

    note = sn.update(args.id, **kwargs)

    if note:
        print(f"\n✅ Updated: {note.id} — {note.title}")
    else:
        print(f"\n❌ Note not found: {args.id}")


def cmd_delete(args):
    """Delete a note."""
    sn = get_notes()
    note = sn.get(args.id)

    if not note:
        print(f"\n❌ Note not found: {args.id}")
        return

    ok = sn.delete(args.id)
    if ok:
        print(f"\n🗑️  Deleted: {note.id} — {note.title}")
    else:
        print(f"\n❌ Failed to delete: {args.id}")


def cmd_stats(args):
    """Show statistics."""
    sn = get_notes()
    stats = sn.get_statistics()

    print(f"\n📊 SecureNotes Statistics\n{'='*40}")
    print(f"  Total Notes:    {stats['total_notes']}")
    print(f"  Total Words:    {stats['total_words']}")
    print(f"  Total Tags:     {stats['total_tags']}")
    print(f"  Favorites:      {stats['total_favorites']}")
    print(f"  Pinned:         {stats['total_pinned']}")

    if stats["top_tags"]:
        print(f"\n  Top Tags:")
        for tag, count in stats["top_tags"]:
            print(f"    {tag:<20} {count}")

    if stats["by_category"]:
        print(f"\n  By Category:")
        for cat, count in stats["by_category"]:
            print(f"    {cat:<20} {count}")


def cmd_encrypt(args):
    """Encrypt arbitrary text."""
    sn = get_notes()
    encrypted = sn.encrypt_text(args.text)
    print(f"\n🔐 Encrypted\n{'='*40}")
    print(f"  {encrypted[:80]}...")
    print(f"\n  Length: {len(encrypted)} chars")


def cmd_decrypt(args):
    """Decrypt text."""
    sn = get_notes()
    decrypted = sn.decrypt_text(args.encrypted)
    print(f"\n🔓 Decrypted\n{'='*40}")
    print(f"  {decrypted}")


def cmd_backup(args):
    """Export backup."""
    sn = get_notes()
    sn.export_backup(args.output)
    print(f"\n💾 Backup exported to {args.output}")


def cmd_restore(args):
    """Import backup."""
    sn = get_notes()
    sn.import_backup(args.input)
    print(f"\n📥 Backup restored from {args.input}")
    print(f"   Notes: {len(sn)}")


def cmd_categories(args):
    """List categories."""
    print(f"\n📁 Note Categories\n{'='*30}")
    for cat in NoteCategory:
        print(f"  • {cat.value}")


def main():
    parser = argparse.ArgumentParser(
        description="📝 SecureNotes — Encrypted Notes"
    )
    sub = parser.add_subparsers(dest="command")

    # create
    create_p = sub.add_parser("create", help="Create note")
    create_p.add_argument("--title", "-t", required=True)
    create_p.add_argument("--content", "-c", required=True)
    create_p.add_argument("--tags", default="")
    create_p.add_argument("--category", default="general")
    create_p.add_argument("--favorite", action="store_true")
    create_p.add_argument("--pinned", action="store_true")

    # list
    list_p = sub.add_parser("list", help="List notes")
    list_p.add_argument("--category", default="")
    list_p.add_argument("--favorites", action="store_true")
    list_p.add_argument("--pinned", action="store_true")
    list_p.add_argument("--tag", default="")

    # get
    get_p = sub.add_parser("get", help="Get note")
    get_p.add_argument("id")

    # search
    search_p = sub.add_parser("search", help="Search notes")
    search_p.add_argument("query")

    # update
    update_p = sub.add_parser("update", help="Update note")
    update_p.add_argument("id")
    update_p.add_argument("--title", default="")
    update_p.add_argument("--content", default="")
    update_p.add_argument("--tags", default="")
    update_p.add_argument("--category", default="")
    update_p.add_argument("--favorite", type=bool, default=None)
    update_p.add_argument("--pinned", type=bool, default=None)

    # delete
    del_p = sub.add_parser("delete", help="Delete note")
    del_p.add_argument("id")

    # stats
    sub.add_parser("stats", help="Statistics")

    # encrypt
    enc_p = sub.add_parser("encrypt", help="Encrypt text")
    enc_p.add_argument("text")

    # decrypt
    dec_p = sub.add_parser("decrypt", help="Decrypt text")
    dec_p.add_argument("encrypted")

    # backup
    bak_p = sub.add_parser("backup", help="Export backup")
    bak_p.add_argument("--output", "-o", default="backup.enc")

    # restore
    res_p = sub.add_parser("restore", help="Import backup")
    res_p.add_argument("--input", "-i", default="backup.enc")

    # categories
    sub.add_parser("categories", help="List categories")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "create": cmd_create, "list": cmd_list, "get": cmd_get,
        "search": cmd_search, "update": cmd_update, "delete": cmd_delete,
        "stats": cmd_stats, "encrypt": cmd_encrypt, "decrypt": cmd_decrypt,
        "backup": cmd_backup, "restore": cmd_restore, "categories": cmd_categories,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
