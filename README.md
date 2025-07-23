# Telegram Auto Account Giver Bot 🤖

यह Telegram Bot हर 24 घंटे में एक यूजर को दो अलग-अलग अकाउंट randomly देता है।

---

## 🛠 Features
- हर यूजर को हर 24 घंटे में केवल एक बार अकाउंट मिलेगा
- Randomly दो अकाउंट दिए जाते हैं (pre-defined list में से)
- Fast, lightweight और Pyrogram-based
- Future में DB या User Management जोड़ सकते हैं

---

## 📦 Requirements
- Python 3.10+
- Telegram Bot Token
- Pyrogram & TgCrypto

---

## 📥 Installation

### 1. Termux में या किसी भी Linux system पर:
```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install pyrogram tgcrypto
