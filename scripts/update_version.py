import re
import sys
import subprocess

def update_version(version):
    """Updates the version in all the required files."""
    if not version:
        print("Error: Version argument required.")
        print("Usage: python scripts/update_version.py <version>")
        sys.exit(1)

    print(f"Updating version to {version}")

    aiexec_version = version
    aiexec_base_version = "0." + ".".join(version.split(".")[1:])

    print(f"Aiexec version: {aiexec_version}")
    print(f"Aiexec-base version: {aiexec_base_version}")

    # Update main pyproject.toml
    print("Updating main pyproject.toml...")
    with open("pyproject.toml", "r+") as f:
        content = f.read()
        content = re.sub(r'^version = ".*"', f'version = "{aiexec_version}"', content, flags=re.MULTILINE)
        content = re.sub(r'"aiexec-base==.*"', f'"aiexec-base=={aiexec_base_version}"', content)
        f.seek(0)
        f.write(content)
        f.truncate()

    # Update aiexec-base pyproject.toml
    print("Updating aiexec-base pyproject.toml...")
    with open("api/base/pyproject.toml", "r+") as f:
        content = f.read()
        content = re.sub(r'^version = ".*"', f'version = "{aiexec_base_version}"', content, flags=re.MULTILINE)
        f.seek(0)
        f.write(content)
        f.truncate()

    # Update frontend package.json
    print("Updating frontend package.json...")
    with open("web/package.json", "r+") as f:
        content = f.read()
        content = re.sub(r'"version": ".*"', f'"version": "{aiexec_version}"', content)
        f.seek(0)
        f.write(content)
        f.truncate()

    print("Validating version changes...")
    # Validations
    with open("pyproject.toml") as f:
        content = f.read()
        if f'version = "{aiexec_version}"' not in content:
            print("✗ Main pyproject.toml version validation failed")
            sys.exit(1)
        if f'"aiexec-base=={aiexec_base_version}"' not in content:
            print("✗ Main pyproject.toml aiexec-base dependency validation failed")
            sys.exit(1)

    with open("api/base/pyproject.toml") as f:
        if f'version = "{aiexec_base_version}"' not in f.read():
            print("✗ Aiexec-base pyproject.toml version validation failed")
            sys.exit(1)

    with open("web/package.json") as f:
        if f'"version": "{aiexec_version}"' not in f.read():
            print("✗ Frontend package.json version validation failed")
            sys.exit(1)

    print("✓ All versions updated successfully")

    print("Syncing dependencies in parallel...")
    p1 = subprocess.Popen(["uv", "sync", "--quiet"])
    p2 = subprocess.Popen(["npm", "install", "--silent"], cwd="web")
    p1.wait()
    p2.wait()

    print("Validating final state...")
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    changed_files = result.stdout.strip().split("\n")
    
    if len(changed_files) < 5:
        print(f"✗ Expected at least 5 changed files, but found {len(changed_files)}")
        print("Changed files:")
        print(result.stdout)
        sys.exit(1)

    expected_files = ["pyproject.toml", "uv.lock", "api/base/pyproject.toml", "web/package.json", "web/package-lock.json"]
    for file in expected_files:
        if not any(file in f for f in changed_files):
            print(f"✗ Expected file {file} was not modified")
            sys.exit(1)
    
    print("✓ All required files were modified.")
    print("Version update complete!")
    print("Updated files:")
    print(f"  - pyproject.toml: {aiexec_version}")
    print(f"  - api/base/pyproject.toml: {aiexec_base_version}")
    print(f"  - web/package.json: {aiexec_version}")
    print("  - uv.lock: dependency lock updated")
    print("  - web/package-lock.json: dependency lock updated")
    print("Dependencies synced successfully!")

if __name__ == "__main__":
    update_version(sys.argv[1] if len(sys.argv) > 1 else "")
