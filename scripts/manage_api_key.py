#!/usr/bin/env python

"""
Manage a Google API key (referrer + API restrictions) stored in `pass`.

Originally written for the calendar API key, but project-specific details
are no longer hardcoded: they default to the calendar values below and can
be overridden via flags or the matching environment variables.

Subcommands:
  show      Show current API key details and restrictions
  restrict  Set HTTP referrer + API restrictions on the existing key
  create    Create a new API key with restrictions, store it in pass
  delete    Delete the current API key from GCP and pass
  rotate    Create a new key, write it into static/keys.js, then (after you
            rebuild and deploy) store it in pass and delete the old one

Configuration (flag / env var / default):
  --project-id   API_KEY_PROJECT_ID    veltzer-calendar-id
  --pass-path    API_KEY_PASS_PATH     cloud/gcp/calendar
  --referrer     API_KEY_REFERRER      veltzer.org/*
  --api-service  API_KEY_API_SERVICE   calendar-json.googleapis.com
  --display-name API_KEY_DISPLAY_NAME  calendar-api-key
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# static/keys.js carries the key in the clear, by design: it is referrer- and
# API-restricted (doc/DECISIONS.md). pass stays the only store for the secret
# itself; this file is the published copy the deployed site reads.
KEYS_JS = Path(__file__).resolve().parent.parent / "static" / "keys.js"
KEYS_JS_RE = re.compile(r"(const API_KEY = ')[^']*(')")

DEFAULTS = {
    "project_id": "veltzer-calendar-id",
    "pass_path": "cloud/gcp/calendar",
    "referrer": "veltzer.org/*",
    "api_service": "calendar-json.googleapis.com",
    "display_name": "calendar-api-key",
}

ENV_VARS = {
    "project_id": "API_KEY_PROJECT_ID",
    "pass_path": "API_KEY_PASS_PATH",
    "referrer": "API_KEY_REFERRER",
    "api_service": "API_KEY_API_SERVICE",
    "display_name": "API_KEY_DISPLAY_NAME",
}


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def run(cmd, *, capture=False, check=True):
    """Run a command, optionally capturing stdout. Returns stdout (stripped) when captured."""
    result = subprocess.run(cmd, check=check, text=True, capture_output=capture)
    if capture:
        return result.stdout.strip()
    return None


def pass_show(pass_path):
    """Read a secret from pass, returning '' if it is not present."""
    result = subprocess.run(
        ["pass", "show", pass_path], text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def pass_insert(pass_path, secret):
    proc = subprocess.run(
        ["pass", "insert", "-e", "-f", pass_path],
        input=f"{secret}\n",
        text=True,
        check=True,
    )
    return proc


def find_key_name(cfg, api_key):
    """Find the key's resource name by matching the stored key string."""
    names = run(
        ["gcloud", "services", "api-keys", "list", f"--project={cfg.project_id}", "--format=value(name)"],
        capture=True,
    )
    for name in names.split():
        key = run(
            ["gcloud", "services", "api-keys", "get-key-string", name, "--format=value(keyString)"],
            capture=True,
            check=False,
        )
        if key == api_key:
            return name
    return ""


def write_keys_js(key_string, path=KEYS_JS):
    """Replace the API_KEY constant in static/keys.js. Raises if it is not there."""
    text = path.read_text(encoding="utf-8")
    new_text, count = KEYS_JS_RE.subn(lambda m: f"{m.group(1)}{key_string}{m.group(2)}", text)
    if count != 1:
        raise ValueError(f"expected exactly one 'const API_KEY' in {path}, found {count}")
    path.write_text(new_text, encoding="utf-8")


def create_key(cfg, store=True):
    """Create a restricted key; return (resource name, key string).

    With store=True the key goes into pass as well. rotate passes store=False:
    the old key must stay in pass until the new one is live and the old one
    is about to be deleted.
    """
    print(f"Creating new API key in project {cfg.project_id}...")
    key_name = run(
        [
            "gcloud", "services", "api-keys", "create",
            f"--project={cfg.project_id}",
            f"--display-name={cfg.display_name}",
            f"--allowed-referrers={cfg.referrer}",
            f"--api-target=service={cfg.api_service}",
            "--format=value(response.name)",
        ],
        capture=True,
    )
    print(f"Created key resource: {key_name}")
    key_string = run(
        ["gcloud", "services", "api-keys", "get-key-string", key_name, f"--project={cfg.project_id}", "--format=value(keyString)"],
        capture=True,
    )
    if store:
        print(f"Storing key in pass at {cfg.pass_path}...")
        pass_insert(cfg.pass_path, key_string)
    return key_name, key_string


def require_api_key(cfg):
    api_key = pass_show(cfg.pass_path)
    if not api_key:
        die(f"No API key found in pass at {cfg.pass_path}")
    return api_key


def require_key_name(cfg, api_key):
    print(f"Looking up API key in project {cfg.project_id}...")
    key_name = find_key_name(cfg, api_key)
    if not key_name:
        die(f"Could not find key matching stored key in project {cfg.project_id}")
    print(f"Key resource: {key_name}")
    return key_name


def cmd_show(cfg):
    api_key = require_api_key(cfg)
    key_name = require_key_name(cfg, api_key)
    print("\n=== Key Details ===")
    run(["gcloud", "services", "api-keys", "describe", key_name, f"--project={cfg.project_id}"])


def cmd_restrict(cfg):
    api_key = require_api_key(cfg)
    key_name = require_key_name(cfg, api_key)
    print("\nSetting restrictions:")
    print(f"  - HTTP referrer: {cfg.referrer}")
    print(f"  - API service:   {cfg.api_service}\n")
    run([
        "gcloud", "services", "api-keys", "update", key_name,
        f"--project={cfg.project_id}",
        f"--allowed-referrers={cfg.referrer}",
        f"--api-target=service={cfg.api_service}",
    ])
    print("\nDone. Verifying:")
    run(["gcloud", "services", "api-keys", "describe", key_name, f"--project={cfg.project_id}"])


def cmd_create(cfg):
    key_name, _ = create_key(cfg)
    print("\n=== New API Key ===")
    print(f"Key stored in pass at: {cfg.pass_path}")
    print(f"Resource: {key_name}")
    print("\nRestrictions applied:")
    print(f"  - HTTP referrer: {cfg.referrer}")
    print(f"  - API service:   {cfg.api_service}")


def cmd_delete(cfg):
    api_key = require_api_key(cfg)
    key_name = require_key_name(cfg, api_key)
    print("\nDeleting API key from GCP...")
    run(["gcloud", "services", "api-keys", "delete", key_name, f"--project={cfg.project_id}"])
    print("\nRemoving key from pass...")
    run(["pass", "rm", "-f", cfg.pass_path])
    print("\nDone. API key deleted from GCP and pass.")


def cmd_rotate(cfg):
    old_api_key = pass_show(cfg.pass_path)
    if not old_api_key:
        print("No existing key found in pass. Running create instead.")
        cmd_create(cfg)
        return
    old_key_name = find_key_name(cfg, old_api_key)
    if not old_key_name:
        print("WARNING: Could not find old key in GCP (may already be deleted)", file=sys.stderr)

    print("=== Creating new API key ===")
    new_key_name, new_key = create_key(cfg, store=False)
    # static/keys.js carries the calendar key and no other: a rotation of any
    # other pass entry leaves the file alone and says so.
    is_site_key = cfg.pass_path == DEFAULTS["pass_path"]
    try:
        if is_site_key:
            write_keys_js(new_key)
            print(f"New key written to {KEYS_JS}; pass still holds the OLD key.\n")
            input(">>> Rebuild and deploy the site now, then press Enter to store the new key "
                  "in pass and delete the old one <<<")
        else:
            print(f"{KEYS_JS} not touched: {cfg.pass_path} is not the site's calendar key "
                  f"({DEFAULTS['pass_path']}).\n")
            input(">>> Put the new key wherever the old one is used, then press Enter to "
                  "store it in pass and delete the old one <<<")
    except KeyboardInterrupt:
        print(
            "\nInterrupted. State: the new key "
            f"({new_key_name}) exists in GCP and, if it got that far, in "
            f"{KEYS_JS}; pass at {cfg.pass_path} still holds the OLD key, and the "
            f"old key ({old_key_name or 'not found in GCP'}) is NOT deleted. Nothing "
            "is orphaned: finish by hand (put the new key in pass, delete the old "
            "key) or delete the new key and revert static/keys.js.",
            file=sys.stderr,
        )
        sys.exit(130)
    print()

    print(f"Storing the new key in pass at {cfg.pass_path}...")
    pass_insert(cfg.pass_path, new_key)
    if old_key_name:
        print("=== Deleting old API key ===")
        run(["gcloud", "services", "api-keys", "delete", old_key_name, f"--project={cfg.project_id}"])
        print("Old key deleted.")
    print("\nDone. Key rotation complete.")


COMMANDS = {
    "show": cmd_show,
    "restrict": cmd_restrict,
    "create": cmd_create,
    "delete": cmd_delete,
    "rotate": cmd_rotate,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Manage a Google API key (referrer + API restrictions) stored in pass.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=COMMANDS, help="action to perform")

    def env_default(field):
        return os.environ.get(ENV_VARS[field], DEFAULTS[field])

    parser.add_argument("--project-id", default=env_default("project_id"), help="GCP project ID")
    parser.add_argument("--pass-path", default=env_default("pass_path"), help="pass entry storing the key")
    parser.add_argument("--referrer", default=env_default("referrer"), help="allowed HTTP referrer")
    parser.add_argument("--api-service", default=env_default("api_service"), help="restricted API service host")
    parser.add_argument("--display-name", default=env_default("display_name"), help="key display name (create/rotate)")
    return parser.parse_args()


def main():
    cfg = parse_args()

    if shutil.which("pass") is None:
        die("'pass' (password-store) is not installed or not in PATH")
    if shutil.which("gcloud") is None:
        die("'gcloud' is not installed or not in PATH")

    try:
        COMMANDS[cfg.command](cfg)
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
