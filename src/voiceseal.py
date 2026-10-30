#!/usr/bin/env python3
"""
VoiceSeal — local-first voice-note sealer for QuantumGuard CONTRACT-v1 packs.
Compatible with the Operator Pages suite. Offline after key setup.
"""
import argparse
import json
import hashlib
import base64
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Note: cryptography not installed. Using stub signatures. pip install cryptography for real Ed25519.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_or_create_key(key_path: Path):
    if not CRYPTO_AVAILABLE:
        return None, "00" * 32
    if key_path.exists():
        with open(key_path, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return priv, pub_bytes.hex()
    else:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem)
        return priv, pub_bytes.hex()

def sign_payload(priv, payload_hash_hex: str) -> str:
    if not CRYPTO_AVAILABLE or priv is None:
        return "00" * 64
    hash_bytes = bytes.fromhex(payload_hash_hex)
    sig = priv.sign(hash_bytes)
    return sig.hex()

def build_evidence_pack(note: dict, priv, pub_hex: str) -> dict:
    payload_obj = {
        "version": "1",
        "type": "voice_note",
        "note_id": note.get("note_id", "unknown"),
        "job_id": note.get("job_id", ""),
        "client": note.get("client", ""),
        "location": note.get("location", ""),
        "transcript": note.get("transcript", ""),
        "language": note.get("language", "en-US"),
        "duration_sec": note.get("duration_sec"),
        "audio_sha256": note.get("audio_sha256", ""),
        "captured_at": note.get("captured_at", ""),
        "operator": note.get("operator", "field-tech"),
        "reviewed": note.get("reviewed", True),
        "tags": note.get("tags", []),
        "sealed_at": note.get("sealed_at", datetime.now(timezone.utc).isoformat()),
        "notes": note.get("notes", "")
    }
    payload_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    payload_hash = sha256_hex(payload_bytes)
    signature = sign_payload(priv, payload_hash)

    return {
        "version": "1",
        "payload": payload_b64,
        "payload_hash": payload_hash,
        "signature": signature,
        "public_key": pub_hex,
        "alg": "ed25519"
    }

def demo():
    sample = {
        "note_id": "VN-2026-011",
        "job_id": "JOB-2026-042",
        "client": "Acme Property Management",
        "location": "123 Main St, Springfield MO — RTU-3",
        "transcript": "Replaced capacitor on RTU-3. Unit cooling properly. Customer walked the roof with me and signed off. Recommend surge protection next visit.",
        "language": "en-US",
        "duration_sec": 28,
        "audio_sha256": "",
        "captured_at": "2026-10-29T15:42:00+00:00",
        "operator": "tech-dan",
        "reviewed": True,
        "tags": ["closeout", "hvac"],
        "notes": "Dictated on-site after completion."
    }
    key_path = Path.home() / ".voiceseal_key.pem"
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(sample, priv, pub_hex)
    print(json.dumps(pack, indent=2))
    print("\n# Verify with: qg verify <this.json>  (from QuantumGuard)")

def main():
    parser = argparse.ArgumentParser(description="VoiceSeal — local voice-note evidence sealer")
    parser.add_argument("--demo", action="store_true", help="Run demo and print sealed pack")
    parser.add_argument("--note", type=str, help="Path to voice-note JSON file")
    parser.add_argument("--out", type=str, help="Output sealed pack path")
    parser.add_argument("--key", type=str, default=str(Path.home() / ".voiceseal_key.pem"), help="Private key path")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not args.note:
        parser.print_help()
        return

    with open(args.note) as f:
        note = json.load(f)

    key_path = Path(args.key)
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(note, priv, pub_hex)

    out_path = args.out or f"sealed_voice_{note.get('note_id', 'unknown')}.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Sealed voice note written to {out_path}")
    print(f"Payload hash: {pack['payload_hash']}")
    print("Verify with QuantumGuard: qg verify", out_path)

if __name__ == "__main__":
    main()
