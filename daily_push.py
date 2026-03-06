"""
NCAAB Daily Push — Run bot + build dashboard + push to GitHub Pages

FIRST-TIME SETUP (run once):
  1. Install Git: https://git-scm.com/download/win (use all defaults)
  2. Open a NEW terminal after installing, then:

     cd C:\\Users\\13032\\Downloads\\NCAAB
     git init
     git remote add origin https://github.com/YOURUSERNAME/ncaab.git
     git branch -M main
     git pull origin main
     git add .
     git commit -m "initial"
     git push -u origin main

  3. Git will ask for your GitHub username and a "personal access token"
     (NOT your password). To get a token:
     - GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
     - Generate new token → check "repo" → copy the token
     - Paste it as your password when git asks

DAILY USE (after setup):
  python daily_push.py

That's it. Bot runs, dashboard builds, site updates.
Your friends see it at: https://YOURUSERNAME.github.io/ncaab/dashboard.html
"""
import subprocess, sys, os
from pathlib import Path

def run(cmd, check=True):
    print(f"  > {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip():
        print(f"    {r.stdout.strip()}")
    if r.returncode != 0 and check:
        print(f"    ERROR: {r.stderr.strip()}")
    return r.returncode == 0

def main():
    os.chdir(Path(__file__).parent)

    print("=" * 50)
    print("  NCAAB DAILY PUSH")
    print("=" * 50)

    # Step 1: Run bot
    print("\n[1/3] Running bot...")
    if not run("python ncaab_bot.py", check=False):
        print("  Bot had issues but continuing...")

    # Step 2: Build dashboard
    print("\n[2/3] Building dashboard...")
    run("python build_dashboard.py")

    # Also copy as index.html so the URL is cleaner
    if Path("dashboard.html").exists():
        import shutil
        shutil.copy2("dashboard.html", "index.html")
        print("  Also created index.html")

    # Step 3: Git push
    print("\n[3/3] Pushing to GitHub...")

    # Check if git is set up
    if not Path(".git").exists():
        print("  ERROR: Git not initialized yet.")
        print("  Run these commands first:")
        print("    git init")
        print("    git remote add origin https://github.com/YOURUSERNAME/ncaab.git")
        print("    git branch -M main")
        print("    git add .")
        print("    git commit -m \"initial\"")
        print("    git push -u origin main")
        return

    from datetime import date
    today = date.today().isoformat()

    run("git add dashboard.html index.html output/latest.json", check=False)
    run(f'git commit -m "Daily update {today}"', check=False)

    if run("git push", check=False):
        print(f"\n  ✓ Site updated!")
        # Try to figure out the remote URL
        r = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            url = r.stdout.strip()
            # Convert git URL to pages URL
            if "github.com" in url:
                # https://github.com/user/repo.git → https://user.github.io/repo/
                parts = url.replace("https://github.com/", "").replace(".git", "").split("/")
                if len(parts) >= 2:
                    pages_url = f"https://{parts[0]}.github.io/{parts[1]}/dashboard.html"
                    print(f"  Your friends' link: {pages_url}")
    else:
        print("  Push failed — check your git setup")
        print("  You may need to run: git push -u origin main")

    print("\n" + "=" * 50)
    print("  Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
