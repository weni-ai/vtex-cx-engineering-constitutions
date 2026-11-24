#!/usr/bin/env python3
"""Resolve Spec Kit feature artifacts, active review lenses, and git diff scope."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, NoReturn

KNOWN_DOMAINS = (
    "backend",
    "frontend",
    "frontend-platform",
)

DOMAIN_ROOT_DIRECTORIES = {
    "backend": "backend",
    "frontend": "frontend",
}

FRONTEND_EXTENSIONS = (
    ".vue", ".tsx", ".jsx", ".ts", ".mts", ".cts", ".js", ".mjs", ".cjs",
    ".scss", ".sass", ".less", ".css",
)

BACKEND_EXTENSIONS = (".py", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".sql")

FRONTEND_DIRECTORY_MARKERS = ("locales",)

FRONTEND_DIRECTORY_SEQUENCES = (
    ("src", "components"),
    ("src", "views"),
    ("src", "pages"),
)

BACKEND_DIRECTORY_MARKERS = ("migrations", "usecases", "serializers")

FENCE_MARKERS = ("```", "~~~")

BASE_REF_CANDIDATES = (
    "origin/main",
    "origin/master",
    "main",
    "master",
    "origin/develop",
    "develop",
)

HELP_TEXT = """Usage: resolve_review_context.py [--json] [--base <git-ref>]

Resolve feature artifacts, constitution domains, open tasks, and git change scope
for the VTEX CX adversarial code review extension.
"""


def fail(*lines: str) -> NoReturn:
    for line in lines:
        print(line, file=sys.stderr)
    raise SystemExit(1)


def parse_args(argv: list[str]) -> tuple[bool, str]:
    json_mode = False
    base_override = ""
    index = 0
    while index < len(argv):
        arg = argv[index]
        lowered = arg.lower()
        if lowered in ("--json", "-json"):
            json_mode = True
        elif lowered in ("--help", "-h", "-help"):
            print(HELP_TEXT, end="")
            raise SystemExit(0)
        elif lowered in ("--base", "-base"):
            if index + 1 >= len(argv):
                fail("ERROR: --base requires a git ref argument.")
            base_override = argv[index + 1]
            index += 1
        elif lowered.startswith("--base="):
            base_override = arg.split("=", 1)[1]
        else:
            fail(f"ERROR: Unknown option '{arg}'. Use --help for usage information.")
        index += 1
    return json_mode, base_override


def find_specify_root(start_dir: Path | None = None) -> Path | None:
    current = (start_dir or Path.cwd()).resolve()
    while True:
        if (current / ".specify").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def resolve_project_root(script_file: Path) -> Path:
    explicit_dir = os.environ.get("SPECIFY_INIT_DIR", "")
    if explicit_dir:
        candidate = Path(explicit_dir)
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            resolved = None
        if resolved is None or not resolved.is_dir():
            fail(f"ERROR: SPECIFY_INIT_DIR does not point to an existing directory: {explicit_dir}")
        if not (resolved / ".specify").is_dir():
            fail(f"ERROR: SPECIFY_INIT_DIR is not a Spec Kit project (no .specify/): {resolved}")
        return resolved

    for candidate_start in (Path.cwd(), script_file.resolve().parent):
        found = find_specify_root(candidate_start)
        if found is not None:
            return found

    fail("ERROR: Not inside a Spec Kit project (no .specify/ directory found).")


def run_git(repo_root: Path, *args: str, check: bool = True) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        fail(f"ERROR: 'git {' '.join(args)}' failed: {result.stderr.strip()}")
    return result.returncode, result.stdout.strip()


def run_git_paths(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"ERROR: 'git {' '.join(args)}' failed: {result.stderr.strip()}")
    return [path for path in result.stdout.split("\0") if path]


def read_feature_directory_from_state(repo_root: Path) -> str:
    feature_json = repo_root / ".specify" / "feature.json"
    if not feature_json.is_file():
        return ""
    try:
        payload = json.loads(feature_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ""
    value = payload.get("feature_directory") if isinstance(payload, dict) else None
    return value if isinstance(value, str) else ""


def infer_feature_directory_from_branch(repo_root: Path) -> str:
    code, branch = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD", check=False)
    if code != 0 or not branch or branch == "HEAD":
        return ""
    tail = branch.rsplit("/", 1)[-1]
    match = re.match(r"^(\d{8}-\d{6}|\d{3,})-", tail)
    if not match:
        return ""
    prefix = match.group(1)
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return ""
    matches = sorted(
        entry for entry in specs_dir.iterdir()
        if entry.is_dir() and entry.name.startswith(f"{prefix}-")
    )
    if len(matches) == 1:
        return matches[0].relative_to(repo_root).as_posix()
    return ""


def resolve_feature_directory(repo_root: Path) -> Path:
    raw = (
        os.environ.get("SPECIFY_FEATURE_DIRECTORY", "")
        or read_feature_directory_from_state(repo_root)
        or infer_feature_directory_from_branch(repo_root)
    )
    if not raw:
        fail(
            "ERROR: Active feature directory could not be resolved.",
            "Run /speckit-specify first or set SPECIFY_FEATURE_DIRECTORY.",
        )
    feature_dir = Path(raw) if Path(raw).is_absolute() else repo_root / raw
    if not feature_dir.is_dir():
        fail(f"ERROR: Feature directory does not exist: {feature_dir}")
    return feature_dir


def is_unfilled_constitution_template(text: str) -> bool:
    placeholder_tokens = ("[PROJECT_NAME]", "[PRINCIPLE_1_NAME]", "[GOVERNANCE_RULES]")
    return any(token in text for token in placeholder_tokens)


def extract_domains_from_text(raw: str) -> list[str]:
    cleaned = raw.lower()
    found: list[str] = []
    for domain in sorted(KNOWN_DOMAINS, key=len, reverse=True):
        if re.search(rf"(?<![a-z0-9-]){re.escape(domain)}(?![a-z0-9-])", cleaned):
            found.append(domain)
    return found


def detect_declared_domains(repo_root: Path, constitution_text: str, spec_text: str) -> list[str]:
    declared: list[str] = []
    for line in constitution_text.splitlines():
        match = re.search(r"^\s*-\s*Domains\s*:\s*(.+)$", line, flags=re.IGNORECASE)
        if match:
            declared.extend(extract_domains_from_text(match.group(1)))

    for line in spec_text.splitlines():
        if line.strip().startswith("**Repository**:") and "[" not in line:
            declared.extend(extract_domains_from_text(line))

    package_json = repo_root / "package.json"
    if package_json.is_file():
        try:
            pkg_text = package_json.read_text(encoding="utf-8")
        except OSError:
            pkg_text = ""
        if "@weni/unnnic-system" in pkg_text and "frontend-platform" not in declared:
            declared.append("frontend-platform")

    return deduplicate_preserving_order(declared)


def parse_tasks_state(tasks_path: Path) -> dict[str, Any]:
    text = tasks_path.read_text(encoding="utf-8")
    open_ids: list[str] = []
    open_count = 0
    max_task_id = 0
    max_phase = 0

    checkbox_pattern = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s*(?P<body>.+)$")
    task_id_pattern = re.compile(r"\bT(\d{3,})\b")
    phase_pattern = re.compile(r"^##\s+Phase\s+(\d+)\b", flags=re.IGNORECASE)
    open_fence = ""

    for line in text.splitlines():
        stripped = line.lstrip()
        fence = next((marker for marker in FENCE_MARKERS if stripped.startswith(marker)), "")
        if fence and (not open_fence or fence == open_fence):
            open_fence = "" if open_fence else fence
            continue
        if open_fence:
            continue

        phase_match = phase_pattern.match(line)
        if phase_match:
            max_phase = max(max_phase, int(phase_match.group(1)))
            continue

        checkbox_match = checkbox_pattern.match(line)
        if not checkbox_match:
            continue

        body = checkbox_match.group("body")
        ids_in_line = [int(num) for num in task_id_pattern.findall(body)]
        if ids_in_line:
            max_task_id = max(max_task_id, *ids_in_line)

        if checkbox_match.group("mark") == " ":
            open_count += 1
            first_id = task_id_pattern.search(body)
            open_ids.append(first_id.group(0) if first_id else body[:40].strip())

    return {
        "open_count": open_count,
        "open_task_ids": open_ids,
        "max_task_id": max_task_id,
        "next_task_id": f"T{max_task_id + 1:03d}",
        "next_phase_number": max_phase + 1,
    }


def resolve_base_ref(repo_root: Path, base_override: str) -> str:
    if base_override:
        code, _ = run_git(repo_root, "rev-parse", "--verify", "--quiet", base_override, check=False)
        if code != 0:
            fail(f"ERROR: Base git ref '{base_override}' could not be resolved.")
        return base_override

    for candidate in BASE_REF_CANDIDATES:
        code, _ = run_git(repo_root, "rev-parse", "--verify", "--quiet", candidate, check=False)
        if code == 0:
            return candidate
    return ""


def split_nonempty_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.strip()]


def is_spec_or_tooling_artifact(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized.removeprefix("./")
    return normalized.startswith(
        (
            ".specify/",
            "specs/",
            ".cursor/",
            ".claude/",
            ".agents/",
            ".codex/",
            ".gemini/",
            ".windsurf/",
        )
    )


def collect_git_scope(repo_root: Path, base_override: str) -> dict[str, Any]:
    code, _ = run_git(repo_root, "rev-parse", "--is-inside-work-tree", check=False)
    if code != 0:
        fail(f"ERROR: Not a git repository: {repo_root}")

    _, toplevel = run_git(repo_root, "rev-parse", "--show-toplevel")
    git_root = Path(toplevel)
    _, branch = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD", check=False)
    base_ref = resolve_base_ref(repo_root, base_override)
    merge_base = ""
    branch_commits: list[str] = []
    committed_files: list[str] = []

    if base_ref:
        mb_code, mb_out = run_git(repo_root, "merge-base", base_ref, "HEAD", check=False)
        _, head_sha = run_git(repo_root, "rev-parse", "HEAD", check=False)
        if mb_code == 0 and mb_out:
            merge_base = mb_out
            if merge_base != head_sha:
                _, log_out = run_git(repo_root, "log", "--oneline", f"{merge_base}..HEAD")
                branch_commits = split_nonempty_lines(log_out)
                committed_files = sorted(
                    run_git_paths(repo_root, "diff", "-z", "--name-only", f"{merge_base}...HEAD")
                )

    staged_files = sorted(run_git_paths(repo_root, "diff", "-z", "--cached", "--name-only"))
    unstaged_files = sorted(run_git_paths(repo_root, "diff", "-z", "--name-only"))
    untracked_files = sorted(
        run_git_paths(repo_root, "ls-files", "-z", "--others", "--exclude-standard", "--full-name")
    )

    all_changed = sorted({*committed_files, *staged_files, *unstaged_files, *untracked_files})
    code_paths = [path for path in all_changed if not is_spec_or_tooling_artifact(path)]
    code_changed = [path for path in code_paths if (git_root / path).exists()]
    deleted_code = [path for path in code_paths if not (git_root / path).exists()]

    return {
        "branch": branch,
        "base_ref": base_ref or None,
        "merge_base": merge_base or None,
        "branch_commits": branch_commits,
        "committed_files": committed_files,
        "staged_files": staged_files,
        "unstaged_files": unstaged_files,
        "untracked_files": untracked_files,
        "all_changed_files": all_changed,
        "code_changed_files": code_changed,
        "deleted_code_files": deleted_code,
    }


def contains_sequence(segments: list[str], sequence: tuple[str, ...]) -> bool:
    width = len(sequence)
    return any(tuple(segments[i:i + width]) == sequence for i in range(len(segments) - width + 1))


def infer_domain_from_path(raw_path: str) -> str | None:
    segments = raw_path.replace("\\", "/").lower().split("/")
    directories, name = segments[:-1], segments[-1]

    for directory in directories:
        if directory in DOMAIN_ROOT_DIRECTORIES:
            return DOMAIN_ROOT_DIRECTORIES[directory]

    if name.endswith(FRONTEND_EXTENSIONS):
        return "frontend"
    if name.endswith(BACKEND_EXTENSIONS):
        return "backend"

    if any(directory in FRONTEND_DIRECTORY_MARKERS for directory in directories) or any(
        contains_sequence(directories, sequence) for sequence in FRONTEND_DIRECTORY_SEQUENCES
    ):
        return "frontend"
    if any(directory in BACKEND_DIRECTORY_MARKERS for directory in directories):
        return "backend"
    return None


def infer_domains_from_files(code_files: list[str]) -> list[str]:
    inferred = [infer_domain_from_path(path) for path in code_files]
    return deduplicate_preserving_order([domain for domain in inferred if domain])


def deduplicate_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def normalize_active_domains(declared: list[str], inferred: list[str]) -> list[str]:
    combined = deduplicate_preserving_order([*declared, *inferred])
    if "frontend-platform" in combined and "frontend" not in combined:
        combined.insert(combined.index("frontend-platform"), "frontend")
    return combined


def render_text_summary(payload: dict[str, Any]) -> str:
    lines = [
        f"REPO_ROOT: {payload['REPO_ROOT']}",
        f"FEATURE_DIR: {payload['FEATURE_DIR']}",
        f"CYCLE: {payload['CYCLE']}",
        f"ACTIVE_DOMAINS: {', '.join(payload['ACTIVE_DOMAINS']) or 'core-only'}",
        f"CODE_CHANGED_FILES: {len(payload['GIT']['code_changed_files'])}",
        f"DELETED_CODE_FILES: {len(payload['GIT']['deleted_code_files'])}",
    ]
    if payload["TASKS_STATE"] is not None:
        lines.append(f"OPEN_TASKS: {payload['TASKS_STATE']['open_count']}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    json_mode, base_override = parse_args(argv)
    repo_root = resolve_project_root(Path(__file__))
    feature_dir = resolve_feature_directory(repo_root)

    spec_path = feature_dir / "spec.md"
    if not spec_path.is_file():
        fail(
            f"ERROR: spec.md not found in {feature_dir}",
            "Run /speckit-specify first to create the Engineering Spec.",
        )

    constitution_path = repo_root / ".specify" / "memory" / "constitution.md"
    if not constitution_path.is_file():
        fail(
            f"ERROR: Repository constitution not found at {constitution_path}",
            "Run the setup-engineering skill first.",
        )

    spec_text = spec_path.read_text(encoding="utf-8")
    constitution_text = constitution_path.read_text(encoding="utf-8")

    plan_path = feature_dir / "plan.md"
    tasks_path = feature_dir / "tasks.md"
    has_tasks = tasks_path.is_file()

    declared_domains = detect_declared_domains(repo_root, constitution_text, spec_text)
    git_scope = collect_git_scope(repo_root, base_override)
    inferred_domains = infer_domains_from_files(
        [*git_scope["code_changed_files"], *git_scope["deleted_code_files"]]
    )
    active_domains = normalize_active_domains(declared_domains, inferred_domains)

    payload: dict[str, Any] = {
        "REPO_ROOT": str(repo_root),
        "FEATURE_DIR": str(feature_dir),
        "SPEC": str(spec_path),
        "PLAN": str(plan_path) if plan_path.is_file() else None,
        "TASKS": str(tasks_path) if has_tasks else None,
        "CONSTITUTION": str(constitution_path),
        "CONSTITUTION_IS_TEMPLATE": is_unfilled_constitution_template(constitution_text),
        "CYCLE": "full" if has_tasks else "lite",
        "DECLARED_DOMAINS": declared_domains,
        "INFERRED_DOMAINS": inferred_domains,
        "ACTIVE_DOMAINS": active_domains,
        "TASKS_STATE": parse_tasks_state(tasks_path) if has_tasks else None,
        "GIT": git_scope,
    }

    if json_mode:
        print(json.dumps(payload))
    else:
        print(render_text_summary(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
