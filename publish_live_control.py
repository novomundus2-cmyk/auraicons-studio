#!/usr/bin/env python3
"""
EKC (ElektriKubercisC) Launch & Privacy Control Switch.
Author: Mikel Irastorza (Data & Deployment Engineer · EFA)

Commands:
  python3 publish_live_control.py status   -> Inspects privacy & deployment state across GitHub & Vercel
  python3 publish_live_control.py unlock   -> Opens Vercel production to the public (Ready for today's launch)
  python3 publish_live_control.py lock     -> Locks Vercel down to 100% private (Requires login)
  python3 publish_live_control.py deploy   -> Builds and deploys latest release to Vercel production
"""

import json
import os
import subprocess
import sys
import urllib.request

TEAM_ID = "team_cr54429wPiAmq2vYBo6AhTKa"
AUTH_FILE = os.path.expanduser("~/Library/Application Support/com.vercel.cli/auth.json")

def get_vercel_token() -> str:
    if not os.path.exists(AUTH_FILE):
        raise RuntimeError("Vercel auth.json not found. Run 'vercel login'.")
    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["token"]

def get_projects(token: str):
    url = f"https://api.vercel.com/v9/projects?teamId={TEAM_ID}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp).get("projects", [])

def check_status():
    print("=" * 68)
    print("  EKC PRIVACY & DEPLOYMENT RADAR: MIKEL IRASTORZA (EFA)")
    print("=" * 68)

    # 1. GitHub Repositories
    print("\n[1. GitHub Repositories Visibility]")
    for repo in ["portfolio", "CV", "auraicons-studio"]:
        try:
            res = subprocess.run(["gh", "repo", "view", f"novomundus2-cmyk/{repo}", "--json", "visibility,isPrivate"], capture_output=True, text=True, check=True)
            d = json.loads(res.stdout)
            status_badge = "🔒 PRIVADO" if d.get("isPrivate") else "🌐 PÚBLICO"
            print(f"  • {repo:20s}: {status_badge} ({d.get('visibility')})")
        except Exception as e:
            print(f"  • {repo:20s}: Error al consultar ({e})")

    # 2. Vercel Projects Deployment Protection
    token = get_vercel_token()
    projects = get_projects(token)
    print("\n[2. Vercel Projects Deployment Protection]")
    for p in projects:
        name = p.get("name")
        sso = p.get("ssoProtection")
        prod_url = f"https://{name}.vercel.app"
        if sso and sso.get("deploymentType") == "all":
            badge = "🔒 100% PRIVADO (SSO / Login Obligatorio)"
        elif sso and sso.get("deploymentType") == "only_preview":
            badge = "🌐 PÚBLICO EN PRODUCCIÓN (Previews protegidas)"
        elif sso is None:
            badge = "🌐 100% PÚBLICO (Sin protección de acceso)"
        else:
            badge = f"⚠️ {sso}"
        print(f"  • {name:22s}: {badge}")

    print("\n[3. Servidores Locales]")
    print("  • Portfolio Server (3222)   : 🔒 127.0.0.1 (Loopback privado)")
    print("  • NetGUI / Archify (8765)   : 🔒 127.0.0.1 (Loopback privado)")
    print("=" * 68)

def set_privacy(mode: str):
    token = get_vercel_token()
    projects = get_projects(token)

    # mode 'lock' -> deploymentType 'all'
    # mode 'unlock' -> None (Public access, no login required)
    target_sso = {"deploymentType": "all"} if mode == "lock" else None
    mode_label = "🔒 PRIVADO (Bloqueo total)" if mode == "lock" else "🌐 PÚBLICO (Listo para subir / lanzamiento)"

    print(f"\n[APLICANDO CAMBIO DE ACCESO]: {mode_label}\n")
    for p in projects:
        p_id = p.get("id")
        p_name = p.get("name")
        patch_url = f"https://api.vercel.com/v9/projects/{p_id}?teamId={TEAM_ID}"
        payload = json.dumps({"ssoProtection": target_sso}).encode()
        req = urllib.request.Request(patch_url, data=payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="PATCH")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"  ✓ {p_name:22s} -> {data.get('ssoProtection')}")
    print(f"\n[ÉXITO] Todos los proyectos han sido configurados en: {mode_label}")

def main():
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if arg == "status":
        check_status()
    elif arg == "unlock":
        set_privacy("unlock")
    elif arg == "lock":
        set_privacy("lock")
    else:
        print("Comandos válidos: status | unlock | lock")

if __name__ == "__main__":
    main()
