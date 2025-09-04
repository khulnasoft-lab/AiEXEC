import re
import shutil
import subprocess
import sys
from pathlib import Path


def update_version(version: str):
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

    try:
        # Update main pyproject.toml
        print("Updating main pyproject.toml...")
        pyproject_file = Path("pyproject.toml")
        content = pyproject_file.read_text()
        content = re.sub(r'^version = ".*"', f'version = "{aiexec_version}"', content, flags=re.MULTILINE)
        content = re.sub(r'"aiexec-base~=.*"', f'"aiexec-base~={aiexec_base_version}"', content)
        pyproject_file.write_text(content)

        # Update aiexec-base pyproject.toml
        print("Updating aiexec-base pyproject.toml...")
        base_file = Path("api/base/pyproject.toml")
        content = base_file.read_text()
        content = re.sub(r'^version = ".*"', f'version = "{aiexec_base_version}"', content, flags=re.MULTILINE)
        base_file.write_text(content)

        # Update frontend package.json
        print("Updating frontend package.json...")
        package_file = Path("web/package.json")
        content = package_file.read_text()
        content = re.sub(r'"version": ".*"', f'"version": "{aiexec_version}"', content)
        package_file.write_text(content)

    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
        sys.exit(1)

    print("Validating version changes...")
    try:
        # Validations
        if f'version = "{aiexec_version}"' not in pyproject_file.read_text():
            print("✗ Main pyproject.toml version validation failed")
            sys.exit(1)
        if f'"aiexec-base~={aiexec_base_version}"' not in pyproject_file.read_text():
            print("✗ Main pyproject.toml aiexec-base dependency validation failed")
            sys.exit(1)
        if f'version = "{aiexec_base_version}"' not in base_file.read_text():
            print("✗ Aiexec-base pyproject.toml version validation failed")
            sys.exit(1)
        if f'"version": "{aiexec_version}"' not in package_file.read_text():
            print("✗ Frontend package.json version validation failed")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"✗ File not found during validation: {e}")
        sys.exit(1)

    print("✓ All versions updated successfully")

    print("Syncing dependencies in parallel...")
    # Validate executables
    uv_exe = shutil.which("uv")
    npm_exe = shutil.which("npm")
    git_exe = shutil.which("git")

    if not uv_exe:
        print("✗ Required executable 'uv' not found in PATH")
        sys.exit(1)
    if not npm_exe:
        print("✗ Required executable 'npm' not found in PATH")
        sys.exit(1)
    if not git_exe:
        print("✗ Required executable 'git' not found in PATH")
        sys.exit(1)

    try:
        # Safe subprocess calls
        subprocess.run([uv_exe, "sync", "--quiet"], check=True)
        subprocess.run([npm_exe, "install", "--silent"], cwd="web", check=True)

    except subprocess.CalledProcessError as e:
        print(f"✗ A subprocess call failed with error: {e}")
        sys.exit(1)

    print("Validating final state...")
    try:
        result = subprocess.run(
            [git_exe, "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"✗ Git command failed with return code {result.returncode}.")
            print(result.stderr)
            sys.exit(1)

        changed_files = result.stdout.strip().split("\n")

    except subprocess.CalledProcessError as e:
        print(f"✗ Git command failed with error: {e}")
        sys.exit(1)

    min_changed_files = 5
    if len(changed_files) < min_changed_files:
        print(f"✗ Expected at least {min_changed_files} changed files, but found {len(changed_files)}")
        print("Changed files:")
        print(result.stdout)
        sys.exit(1)

    expected_files = [
        "pyproject.toml",
        "uv.lock",
        "api/base/pyproject.toml",
        "web/package.json",
        "web/package-lock.json",
    ]
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
