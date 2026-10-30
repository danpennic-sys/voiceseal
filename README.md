# VoiceSeal

**Local-first voice-note capture and QuantumGuard evidence sealer for field operators.**

Browser Web Speech API for capture. Offline CLI for sealing. Deterministic. Pay once.
Compatible with QuantumGuard CONTRACT-v1, MediaSeal, FieldSeal, JobSeal, ChangeOrderSeal, PunchListSeal, CloseSeal, LifecycleSeal, and Evidence-Core.

## Why VoiceSeal?

Field techs dictate notes while hands are dirty or gloves are on. Voice memos on phones are easy to lose, edit, or dispute. VoiceSeal captures a transcript (and optional audio file hash), attaches job context, and seals it into a client-verifiable QuantumGuard evidence pack.

- No SaaS. No cloud transcription required for the core path (browser Web Speech runs on-device).
- Clients verify the sealed pack with the free QuantumGuard verifier (`qg verify`).
- Pairs with MediaSeal (if you also hash the audio file), FieldSeal / JobSeal (job context), and LifecycleSeal (full job).

## Quick Start

### Browser capture (local file)

```bash
# open static/voice.html in a modern browser (Chrome/Edge recommended)
# or serve it:
python3 -m http.server 8080 --directory static
# then http://127.0.0.1:8080/voice.html
```

Speak → review transcript → download JSON → seal with CLI.

### CLI seal

```bash
pip install cryptography   # optional, for real Ed25519

python3 src/voiceseal.py --demo
python3 src/voiceseal.py --note samples/note-001.json --out sealed_voice.json
qg verify sealed_voice.json
```

## What you can sell

| SKU       | Price | Includes                                      |
|-----------|-------|-----------------------------------------------|
| Operator  | $79   | CLI + browser capture page + key guide + 1-year email support |
| Command   | $199  | + batch mode + offline templates + reseller rights |
| Agency    | $499  | + white-label HTML + design partner onboarding |

Purchase / access: danpennic@gmail.com

Source remains free under Apache-2.0 OR MIT. Commercial Operator Pack sold separately.

## Stack Fit

- Python CLI (same family as MediaSeal, FieldSeal, ChangeOrderSeal, PunchListSeal)
- Static HTML + Web Speech API (no build step, same discipline as op-landing)
- Emits QuantumGuard CONTRACT-v1 bundles (Ed25519, deterministic hashing)
- Local key storage (PEM)
- Optional audio file hash via MediaSeal path

## Design constraints

- Core path is local-first: Web Speech in browser; no required remote LLM
- Mic only after user gesture
- Transcript is operator-reviewed before seal (not auto-committed)
- Sealer does not claim speech-to-text accuracy — it seals the reviewed text

## License

Apache-2.0 OR MIT
