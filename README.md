<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/python-3.10+-yellow?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/tests-30-passing-brightgreen?style=for-the-badge">
  <img src="https://img.shields.io/badge/encryption-AES--256-brightgreen?style=for-the-badge">
  <img src="https://img.shields.io/github/stars/0xvanguard/securenotes?style=for-the-badge">
</p>

# 📝 SecureNotes

**AES-256 Encrypted Notes — Private, secure, and organized.**

SecureNotes provides military-grade AES-256 encryption for your notes. Features include categories, favorites, pinning, tag-based organization, relevance-scored search, and encrypted backup/restore.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **AES-256 Encryption** | PBKDF2 key derivation, 480K iterations |
| **8 Categories** | General, Personal, Work, Security, Code, Research, Meeting, TODO |
| **Smart Search** | Relevance-scored search across title, content, tags |
| **Favorites & Pinning** | Star important notes, pin to top |
| **Tag Organization** | Tag-based filtering and search |
| **Encrypted Backup** | Full encrypted export/restore |
| **Word Count** | Automatic word counting |
| **Raw Encryption** | Encrypt/decrypt arbitrary text |

## 🚀 Quick Start

```bash
pip install -r requirements.txt

# Create a note
export SECURENOTES_PASSWORD="my-secret"
python cli.py create -t "My Note" -c "Hello world" --tags work --category security

# List notes
python cli.py list
python cli.py list --category work
python cli.py list --favorites

# Search
python cli.py search "password"

# Get a note
python cli.py get NOTE-0001

# Backup
python cli.py backup -o backup.enc
python cli.py restore -i backup.enc

# Statistics
python cli.py stats
```

## 🐍 Python API

```python
from src.notes import SecureNotes

sn = SecureNotes(master_password="my-secret")

# Create
note = sn.create(title="API Keys", content="sk-123...", tags=["security"], category="security")

# Search
results = sn.search("api")

# Backup
sn.export_backup("backup.enc")

# Raw encryption
encrypted = sn.encrypt_text("secret data")
decrypted = sn.decrypt_text(encrypted)
```

## 🔐 Security

| Feature | Detail |
|---------|--------|
| Algorithm | AES-256 (Fernet) |
| Key Derivation | PBKDF2-HMAC-SHA256 |
| Iterations | 480,000 |
| Salt | Configurable |

## 📁 Structure

```
securenotes/
├── src/
│   ├── __init__.py
│   └── notes.py            # Core engine + encryption
├── tests/
│   └── test_notes.py       # 30 tests
├── cli.py                  # CLI tool
├── requirements.txt
└── README.md
```

## 📄 License

MIT License — see [LICENSE](LICENSE)
