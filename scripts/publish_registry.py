"""Publish server.json to the official MCP Registry with HTTP domain auth.

The registry checks https://<domain>/.well-known/mcp-registry-auth for the
ed25519 public key, then trusts a signed timestamp. Usage:
    python scripts/publish_registry.py <seed_hex_file> [--dry-run]
"""
import base64
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REGISTRY = "https://registry.modelcontextprotocol.io/v0.1"
DOMAIN = "gemstoneaiapp.com"
SERVER_JSON = Path(__file__).resolve().parent.parent / "server.json"


def main() -> int:
    key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(Path(sys.argv[1]).read_text().strip()))
    pub = base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    server = json.loads(SERVER_JSON.read_text())

    proof = httpx.get(f"https://{DOMAIN}/.well-known/mcp-registry-auth", timeout=20)
    if proof.status_code != 200 or f"p={pub}" not in proof.text:
        print(f"proof not live at https://{DOMAIN}/.well-known/mcp-registry-auth (HTTP {proof.status_code}); publish the site first")
        return 1
    print("proof live, key matches")

    check = httpx.post(f"{REGISTRY}/validate", json=server, timeout=30).json()
    if not check.get("valid"):
        print("server.json invalid:", check)
        return 1
    print("server.json valid")
    if "--dry-run" in sys.argv:
        return 0

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    auth = httpx.post(f"{REGISTRY}/auth/http", timeout=30, json={
        "domain": DOMAIN, "timestamp": ts, "signed_timestamp": key.sign(ts.encode()).hex()})
    if auth.status_code != 200:
        print("auth failed:", auth.status_code, auth.text[:400])
        return 1
    token = auth.json()["registry_token"]
    pub_resp = httpx.post(f"{REGISTRY}/publish", json=server, timeout=60, headers={"Authorization": f"Bearer {token}"})
    print("publish:", pub_resp.status_code, pub_resp.text[:600])
    return 0 if pub_resp.status_code in (200, 201) else 1


if __name__ == "__main__":
    sys.exit(main())
