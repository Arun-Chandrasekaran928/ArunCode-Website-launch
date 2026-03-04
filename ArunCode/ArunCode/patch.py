"""
Run this once in your Codespace:
  python patch.py
"""
import os, re

BASE = "/workspaces/ArunCode-Website-launch/ArunCode/ArunCode"
INDEX = os.path.join(BASE, "static", "index.html")
IDE   = os.path.join(BASE, "ide",    "index.html")

# ── Fix 1: index.html — read ?next= and redirect there after boot ──
content = open(INDEX).read()

OLD = "window.location.href = '/home';"
NEW = """const _p = new URLSearchParams(window.location.search);
      const _next = _p.get('next');
      window.location.href = (_next && _next.startsWith('/')) ? _next : '/home';"""

if OLD in content:
    content = content.replace(OLD, NEW)
    open(INDEX, "w").write(content)
    print("✔ index.html patched")
else:
    # Already patched or different text — check
    if "_next" in content:
        print("✔ index.html already patched")
    else:
        # Nuclear option — replace the whole setTimeout block
        content = re.sub(
            r"setTimeout\s*\(\s*\(\s*\)\s*=>\s*\{[\s\S]*?window\.location\.href\s*=\s*['\"].*?['\"];?\s*\},\s*\d+\s*\);",
            """setTimeout(() => {
      sessionStorage.setItem('aruncode_user', pendingUser);
      sessionStorage.setItem('aruncode_role', pendingRole || 'user');
      const _p = new URLSearchParams(window.location.search);
      const _next = _p.get('next');
      window.location.href = (_next && _next.startsWith('/')) ? _next : '/home';
    }, 2900);""",
            content
        )
        open(INDEX, "w").write(content)
        print("✔ index.html patched (nuclear)")

# ── Fix 2: ide/index.html — add ?next=/ide redirect if not logged in ──
content2 = open(IDE).read()

AUTH_SNIPPET = """
  <script>
    // ── AUTH CHECK ──
    (async () => {
      try {
        const me = await fetch('/api/me').then(r => r.json());
        if (!me || !me.ok) {
          window.location.href = '/terminal?next=/ide';
        }
      } catch(e) {
        window.location.href = '/terminal?next=/ide';
      }
    })();
"""

if "next=/ide" in content2:
    print("✔ ide/index.html already has auth check")
elif "<script>" in content2:
    content2 = content2.replace("<script>", AUTH_SNIPPET, 1)
    open(IDE, "w").write(content2)
    print("✔ ide/index.html patched")
else:
    print("✖ Could not patch ide/index.html — no <script> tag found")

# ── Verify ──
print("\n--- VERIFY ---")
idx = open(INDEX).read()
print("index.html has _next:", "_next" in idx)
ide_c = open(IDE).read()
print("ide/index.html has next=/ide:", "next=/ide" in ide_c)