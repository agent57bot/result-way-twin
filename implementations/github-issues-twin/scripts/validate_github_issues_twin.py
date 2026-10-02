#!/usr/bin/env python3
"""Validate a GitHub Issues Twin log against the interchange schema and this profile.

The normative record shape is schemas/bve-interchange.schema.json. This script
adds the GitHub Issues Twin profile rules (one Result issue, one fenced
document per node, append-only edits, and provenance identity). It does not
widen or narrow the schema.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[3]
PROFILE_ROOT = Path(__file__).resolve().parents[1]
ACTOR_EXTENSION = "github.com/agent57bot/result-way-protocol:github-issues-actor"
COMMENT_KINDS = {
    "result",
    "plan",
    "review",
    "execution",
    "verification",
    "evaluation",
    "improvement",
    "event",
}
NON_EVENT_KINDS = COMMENT_KINDS - {"event"}
FENCE_RE = re.compile(r"```bve-interchange[^\n]*\n(.*?)\n```", re.DOTALL)
LINK_RE = re.compile(r"^Result-Record:\s+(https://\S+)\s*$", re.MULTILINE)

ISSUE_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String = null) {
  repository(owner: $owner, name: $name) {
    issue(number: $number) {
      body
      lastEditedAt
      author { login }
      comments(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          databaseId
          body
          createdAt
          lastEditedAt
          author { login }
        }
      }
    }
  }
}
"""


class ProfileError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ProfileError([f"{path}: schema is not a valid Draft 2020-12 document: {exc.message}"]) from exc
    return schema


def validator_for(schema: dict) -> Draft202012Validator:
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def extract_fence(body: str, source: str) -> tuple[dict | None, list[str]]:
    """Return the single fenced document, or errors. A missing fence yields (None, [])."""
    if body is None:
        return None, [f"{source}: body is empty"]
    matches = list(FENCE_RE.finditer(body))
    links = LINK_RE.findall(body)
    errors: list[str] = []
    if len(matches) > 1:
        errors.append(f"{source}: expected one bve-interchange fence, found {len(matches)}")
    if len(links) > 1:
        errors.append(f"{source}: expected at most one Result-Record link, found {len(links)}")
    if matches and links:
        errors.append(f"{source}: use either one embedded fence or one Result-Record link")
    if errors:
        return None, errors
    if not matches:
        return None, []
    raw = matches[0].group(1).strip()
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"{source}: fence is not JSON ({exc.msg} at line {exc.lineno})"]
    if not isinstance(document, dict):
        return None, [f"{source}: fence must be a JSON object"]
    return document, []


def schema_errors(document: dict, validator: Draft202012Validator, source: str) -> list[str]:
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = error.json_path or "$"
        errors.append(f"{source}: {location}: {error.message}")
    return errors


def check_provenance(record: dict, source: str) -> list[str]:
    errors: list[str] = []
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        return [f"{source}: record is missing provenance"]
    agent = provenance.get("agent")
    if not isinstance(agent, str) or not agent.strip():
        errors.append(f"{source}: provenance.agent is required by this profile")
    extensions = provenance.get("extensions")
    actor = extensions.get(ACTOR_EXTENSION) if isinstance(extensions, dict) else None
    if not isinstance(actor, dict):
        errors.append(
            f"{source}: provenance.extensions[{ACTOR_EXTENSION!r}] must carry team and role"
        )
        return errors
    for field in ("team", "role"):
        value = actor.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{source}: actor {field} must be a non-empty string")
    producer = provenance.get("producer")
    if record.get("kind") == "review":
        reviewer = (record.get("spec") or {}).get("reviewer")
        if reviewer != producer:
            errors.append(f"{source}: review.spec.reviewer must equal provenance.producer")
    if record.get("kind") == "event":
        actor_name = (record.get("spec") or {}).get("actor")
        if actor_name != producer:
            errors.append(f"{source}: event.spec.actor must equal provenance.producer")
    return errors


class _HttpsOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not str(newurl).startswith("https://"):
            raise urllib.error.HTTPError(req.full_url, code, "redirect left https", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_linked_document(url: str, source: str) -> tuple[dict | None, list[str]]:
    """Fetch one https interchange document for a Result-Record link."""
    if not url.startswith("https://"):
        return None, [f"{source}: Result-Record URL must use https"]
    opener = urllib.request.build_opener(_HttpsOnlyRedirect)
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with opener.open(request, timeout=30) as response:
            raw = response.read(1_000_001)
    except Exception as exc:
        return None, [f"{source}: could not fetch Result-Record link ({exc})"]
    if len(raw) > 1_000_000:
        return None, [f"{source}: Result-Record target is larger than 1000000 bytes"]
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"{source}: Result-Record target is not JSON ({exc})"]
    if not isinstance(document, dict):
        return None, [f"{source}: Result-Record target must be a JSON object"]
    return document, []


def check_document_shape(document: dict, source: str, *, expected_kind: str | None = None) -> list[str]:
    records = document.get("records")
    if not isinstance(records, list):
        return []
    if len(records) != 1:
        return [f"{source}: this profile stores exactly one record per issue body or comment"]
    record = records[0]
    if not isinstance(record, dict):
        return [f"{source}: record must be an object"]
    errors = check_provenance(record, source)
    kind = record.get("kind")
    if expected_kind is not None and kind != expected_kind:
        errors.append(f"{source}: expected kind {expected_kind}, found {kind}")
    if kind in NON_EVENT_KINDS and not isinstance(record.get("version"), int):
        errors.append(f"{source}: {kind} records in this profile include an integer version")
    return errors


def _independent_errors(
    documents: list[tuple[str, dict]],
    validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []
    for source, document in documents:
        local = schema_errors(document, validator, source)
        errors.extend(local)
        if local:
            continue
        errors.extend(check_document_shape(document, source))
    return errors


def _record(document: dict) -> dict:
    return document["records"][0]


def _producer(record: dict) -> str:
    return record["provenance"]["producer"]


def _resolve(records_by_key: dict[tuple[str, int | None], dict], ref: dict, source: str, field: str) -> tuple[dict | None, list[str]]:
    if not isinstance(ref, dict) or "id" not in ref:
        return None, [f"{source}: {field} is missing id"]
    version = ref.get("version")
    key = (ref["id"], version if isinstance(version, int) else None)
    target = records_by_key.get(key)
    if target is None and version is None:
        matches = [item for (record_id, _), item in records_by_key.items() if record_id == ref["id"]]
        if len(matches) == 1:
            target = matches[0]
    if target is None:
        return None, [f"{source}: {field} does not resolve to {ref.get('id')} version {version}"]
    errors = []
    if ref.get("kind") and ref["kind"] != target.get("kind"):
        errors.append(f"{source}: {field} kind {ref['kind']} does not match {target.get('kind')}")
    if isinstance(version, int) and target.get("version") != version:
        errors.append(f"{source}: {field} version {version} does not match the stored record")
    return target, errors


def validate_log(
    nodes: list[dict],
    validator: Draft202012Validator,
    fetch=fetch_linked_document,
) -> list[str]:
    """Validate an issue body followed by comments in append order.

    Each node is {source, body, last_edited_at, created_at, author_login, document}.
    `document` may be supplied for a Result-Record link whose target was already fetched.
    """
    if not nodes:
        return ["log: missing issue body"]
    errors: list[str] = []
    parsed: list[tuple[dict, dict]] = []
    for index, node in enumerate(nodes):
        source = node["source"]
        if node.get("last_edited_at"):
            errors.append(
                f"{source}: edited issue bodies and comments are not authoritative; append a new comment"
            )
            continue
        document = node.get("document")
        extract_errors: list[str] = []
        if document is None:
            document, extract_errors = extract_fence(node.get("body") or "", source)
            errors.extend(extract_errors)
        if document is None and not extract_errors:
            links = LINK_RE.findall(node.get("body") or "")
            if index == 0 and len(links) == 1:
                document, fetch_errors = fetch(links[0], source)
                errors.extend(fetch_errors)
            elif not any(item.startswith(f"{source}:") for item in errors):
                errors.append(f"{source}: missing bve-interchange fence")
        if document is None:
            continue
        local = schema_errors(document, validator, source)
        errors.extend(local)
        if local:
            continue
        expected = "result" if index == 0 else None
        errors.extend(check_document_shape(document, source, expected_kind=expected))
        record = _record(document)
        if index > 0 and record.get("kind") not in COMMENT_KINDS:
            errors.append(f"{source}: comment kind {record.get('kind')} is not part of this profile")
        parsed.append((node, document))

    if errors:
        return errors

    opening = _record(parsed[0][1])
    if opening.get("kind") != "result":
        return [f"{parsed[0][0]['source']}: issue body must hold the opening result"]
    result_id = opening["id"]
    seen: dict[tuple[str, int | None], dict] = {}
    versions: dict[str, int] = {}
    kinds: dict[str, str] = {}
    event_sequence = 0
    plan_versions: dict[int, dict] = {}

    for node, document in parsed:
        source = node["source"]
        record = _record(document)
        kind = record["kind"]
        record_id = record["id"]
        version = record.get("version")
        key = (record_id, version if isinstance(version, int) else None)
        if key in seen:
            errors.append(f"{source}: duplicate record {record_id} version {version}")
            continue
        if record_id in kinds and kinds[record_id] != kind:
            errors.append(f"{source}: id {record_id} already used for kind {kinds[record_id]}")
        if isinstance(version, int) and record_id in versions and version <= versions[record_id]:
            errors.append(
                f"{source}: version {version} of {record_id} does not increase the current version {versions[record_id]}"
            )
        if kind == "result" and record_id != result_id:
            errors.append(f"{source}: this issue already stores result {result_id}")
        if kind == "event":
            sequence = record["spec"]["sequence"]
            if sequence <= event_sequence:
                errors.append(f"{source}: event sequence {sequence} must increase along the comment log")
            event_sequence = sequence
        kinds[record_id] = kind
        if isinstance(version, int):
            versions[record_id] = version
        seen[key] = record
        if kind == "plan" and isinstance(version, int):
            plan_versions[version] = record
        errors.extend(_check_refs(record, seen, result_id, source, plan_versions))

    return errors


def _check_refs(
    record: dict,
    seen: dict[tuple[str, int | None], dict],
    result_id: str,
    source: str,
    plan_versions: dict[int, dict],
) -> list[str]:
    spec = record.get("spec") or {}
    errors: list[str] = []
    kind = record["kind"]

    def require(ref: dict | None, field: str, expected_kind: str | None = None) -> dict | None:
        if not isinstance(ref, dict):
            errors.append(f"{source}: {field} is missing")
            return None
        if expected_kind and ref.get("kind") not in (None, expected_kind):
            errors.append(f"{source}: {field} kind must be {expected_kind}")
        target, resolve_errors = _resolve(seen, ref, source, field)
        errors.extend(resolve_errors)
        return target

    if kind == "plan":
        result = require(spec.get("result_ref"), "spec.result_ref", "result")
        if result is not None and result.get("id") != result_id:
            errors.append(f"{source}: plan result_ref must be {result_id}")
        if spec.get("status") == "approved":
            errors.extend(_check_approved_plan(record, seen, source, plan_versions))
    elif kind == "review":
        require(spec.get("subject_ref"), "spec.subject_ref")
    elif kind == "execution":
        require(spec.get("plan_ref"), "spec.plan_ref", "plan")
    elif kind == "verification":
        result = require(spec.get("result_ref"), "spec.result_ref", "result")
        if result is not None and result.get("id") != result_id:
            errors.append(f"{source}: verification result_ref must be {result_id}")
        require(spec.get("execution_ref"), "spec.execution_ref", "execution")
    elif kind == "evaluation":
        result = require(spec.get("result_ref"), "spec.result_ref", "result")
        if result is not None and result.get("id") != result_id:
            errors.append(f"{source}: evaluation result_ref must be {result_id}")
        require(spec.get("plan_ref"), "spec.plan_ref", "plan")
        require(spec.get("execution_ref"), "spec.execution_ref", "execution")
        if isinstance(spec.get("verification_ref"), dict):
            require(spec["verification_ref"], "spec.verification_ref", "verification")
    elif kind == "improvement":
        for index, ref in enumerate(spec.get("based_on_refs") or []):
            require(ref, f"spec.based_on_refs[{index}]")
    return errors


def _check_approved_plan(
    record: dict,
    seen: dict[tuple[str, int | None], dict],
    source: str,
    plan_versions: dict[int, dict],
) -> list[str]:
    spec = record["spec"]
    refs = spec.get("approval_refs") or []
    errors: list[str] = []
    if not refs:
        return [f"{source}: an approved plan cites one or more passing reviews in approval_refs"]
    previous_versions = [version for version in plan_versions if version < record["version"]]
    if not previous_versions:
        return [f"{source}: an approved plan follows a draft version of the same plan in the log"]
    reviewed_version = max(previous_versions)
    for index, ref in enumerate(refs):
        field = f"spec.approval_refs[{index}]"
        target, resolve_errors = _resolve(seen, ref, source, field)
        errors.extend(resolve_errors)
        if target is None:
            continue
        if target.get("kind") != "review" or (target.get("spec") or {}).get("decision") != "pass":
            errors.append(f"{source}: {field} must resolve to a passing review")
            continue
        subject = (target.get("spec") or {}).get("subject_ref") or {}
        if subject.get("id") != record["id"] or subject.get("version") != reviewed_version:
            errors.append(
                f"{source}: {field} must review {record['id']} version {reviewed_version}, "
                "the plan version immediately before this approval"
            )
            continue
        review_producer = _producer(target)
        authors = {_producer(record), _producer(plan_versions[reviewed_version])}
        if review_producer in authors:
            errors.append(f"{source}: approving review producer {review_producer} must differ from the plan producer")
    return errors


def fences_in_file(path: Path) -> list[tuple[str, dict]]:
    text = path.read_text(encoding="utf-8")
    found = []
    for index, match in enumerate(FENCE_RE.finditer(text), start=1):
        source = f"{path}:{index}"
        try:
            document = json.loads(match.group(1).strip())
        except json.JSONDecodeError as exc:
            raise ProfileError([f"{source}: fence is not JSON ({exc.msg})"]) from exc
        found.append((source, document))
    return found


def nodes_from_markdown(body_path: Path, comments_dir: Path) -> list[dict]:
    nodes = [{"source": str(body_path), "body": body_path.read_text(encoding="utf-8"), "last_edited_at": None}]
    if comments_dir.is_dir():
        for path in sorted(comments_dir.iterdir()):
            if path.suffix == ".md" and path.is_file():
                nodes.append(
                    {"source": str(path), "body": path.read_text(encoding="utf-8"), "last_edited_at": None}
                )
    return nodes


def nodes_from_payload(payload: dict) -> list[dict]:
    issue = payload["issue"]
    nodes = [
        {
            "source": f"issue#{issue.get('number', '')}",
            "body": issue.get("body") or "",
            "last_edited_at": issue.get("last_edited_at"),
            "created_at": issue.get("created_at"),
            "author_login": issue.get("author_login"),
            "document": issue.get("document"),
        }
    ]
    comments = list(payload.get("comments") or [])
    comments.sort(key=lambda item: (item.get("created_at") or "", item.get("id") or 0))
    for comment in comments:
        nodes.append(
            {
                "source": f"comment#{comment.get('id')}",
                "body": comment.get("body") or "",
                "last_edited_at": comment.get("last_edited_at"),
                "created_at": comment.get("created_at"),
                "author_login": comment.get("author_login"),
                "document": comment.get("document"),
            }
        )
    return nodes


def payload_from_graphql(data: dict) -> dict:
    if data.get("errors"):
        messages = "; ".join(error.get("message", "GraphQL error") for error in data["errors"])
        raise ProfileError([messages])
    issue = ((data.get("data") or {}).get("repository") or {}).get("issue")
    if issue is None:
        raise ProfileError(["GitHub issue not found"])
    comments = (issue.get("comments") or {}).get("nodes") or []
    return {
        "issue": {
            "body": issue.get("body") or "",
            "last_edited_at": issue.get("lastEditedAt"),
            "author_login": (issue.get("author") or {}).get("login"),
        },
        "comments": [
            {
                "id": node.get("databaseId"),
                "body": node.get("body") or "",
                "created_at": node.get("createdAt"),
                "last_edited_at": node.get("lastEditedAt"),
                "author_login": (node.get("author") or {}).get("login"),
            }
            for node in comments
        ],
        "page_info": (issue.get("comments") or {}).get("pageInfo") or {},
    }


def fetch_repository_issue(repository: str, number: int) -> dict:
    if "/" not in repository:
        raise ProfileError([f"repository must be owner/name, got {repository!r}"])
    owner, name = repository.split("/", 1)
    cursor = None
    issue_payload: dict | None = None
    comments: list[dict] = []
    while True:
        command = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={ISSUE_QUERY}",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
            "-F",
            f"number={number}",
        ]
        if cursor:
            command.extend(["-f", f"cursor={cursor}"])
        try:
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise ProfileError(["gh is not installed; cannot read the GitHub issue"]) from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise ProfileError([f"gh api graphql failed: {detail}"])
        page = payload_from_graphql(json.loads(completed.stdout))
        if issue_payload is None:
            issue_payload = page["issue"]
        comments.extend(page["comments"])
        page_info = page["page_info"]
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
    assert issue_payload is not None
    return {"issue": issue_payload, "comments": comments}


def collect_template_documents() -> list[tuple[str, dict]]:
    documents: list[tuple[str, dict]] = []
    templates = PROFILE_ROOT / "templates"
    for path in sorted(templates.rglob("*.md")):
        found = fences_in_file(path)
        if not found:
            raise ProfileError([f"{path}: template is missing a bve-interchange fence"])
        documents.extend(found)
    return documents


def run_self_test(schema_path: Path) -> int:
    schema = load_schema(schema_path)
    validator = validator_for(schema)
    errors: list[str] = []

    portable = ROOT / "examples" / "04-portable-interchange" / "artifacts" / "bve-interchange.json"
    with portable.open(encoding="utf-8") as handle:
        portable_document = json.load(handle)
    errors.extend(schema_errors(portable_document, validator, str(portable)))

    try:
        templates = collect_template_documents()
    except ProfileError as exc:
        errors.extend(exc.errors)
        templates = []
    errors.extend(_independent_errors(templates, validator))

    body = PROFILE_ROOT / "examples" / "minimal-log" / "issue.md"
    comments = PROFILE_ROOT / "examples" / "minimal-log" / "comments"
    nodes = nodes_from_markdown(body, comments)
    errors.extend(validate_log(nodes, validator))
    template_pairs = [
        (PROFILE_ROOT / "templates" / "result-issue.md", body),
        (PROFILE_ROOT / "templates" / "comments" / "plan.md", comments / "001-plan.md"),
        (PROFILE_ROOT / "templates" / "comments" / "review-red-team.md", comments / "002-review.md"),
        (PROFILE_ROOT / "templates" / "comments" / "plan-approved.md", comments / "003-plan-approved.md"),
    ]
    for template_path, example_path in template_pairs:
        template_docs = fences_in_file(template_path)
        example_docs = fences_in_file(example_path)
        if [document for _, document in template_docs] != [document for _, document in example_docs]:
            errors.append(f"self-test: {example_path.name} drifted from {template_path.name}")

    payload = {
        "issue": {"number": 1, "body": nodes[0]["body"], "last_edited_at": None, "author_login": "shared-bot"},
        "comments": [
            {
                "id": index,
                "body": node["body"],
                "created_at": f"2026-10-02T13:0{index}:00Z",
                "last_edited_at": None,
                "author_login": "shared-bot",
            }
            for index, node in enumerate(nodes[1:], start=1)
        ],
    }
    errors.extend(validate_log(nodes_from_payload(payload), validator))

    edited = [dict(node) for node in nodes]
    edited[1] = dict(edited[1], last_edited_at="2026-10-02T15:00:00Z")
    if not any("not authoritative" in item for item in validate_log(edited, validator)):
        errors.append("self-test: edited comment was accepted")

    duplicate = nodes + [dict(nodes[2], source="duplicate-review")]
    if not any("duplicate record" in item for item in validate_log(duplicate, validator)):
        errors.append("self-test: duplicate record was accepted")

    prose = [nodes[0], {"source": "prose", "body": "Looks good.", "last_edited_at": None}]
    if not any("missing bve-interchange fence" in item for item in validate_log(prose, validator)):
        errors.append("self-test: prose-only comment was accepted")

    opening_document, opening_errors = extract_fence(nodes[0]["body"], "body")
    if opening_errors or opening_document is None:
        errors.extend(opening_errors or ["self-test: opening fence missing"])
        opening_document = {"records": [{}]}
    missing_actor = json.loads(json.dumps(_record(opening_document)))
    missing_actor["provenance"].pop("extensions", None)
    broken = {
        "format": "bve-interchange",
        "format_version": "1.0",
        "document_id": "example/twin-store/1/broken",
        "created_at": "2026-10-02T13:00:00Z",
        "records": [missing_actor],
    }
    broken_node = [{"source": "missing-actor", "body": "", "document": broken, "last_edited_at": None}]
    # validate_log still schema-checks. The document is schema-valid without the extension.
    if not any("team and role" in item for item in validate_log(broken_node, validator)):
        errors.append("self-test: missing team and role was accepted")

    review_document, review_errors = extract_fence(nodes[2]["body"], "review")
    if review_errors or review_document is None:
        errors.extend(review_errors or ["self-test: review fence missing"])
    else:
        same_author = json.loads(json.dumps(review_document))
        same_author["records"][0]["provenance"]["producer"] = "planner-agent"
        same_author["records"][0]["provenance"]["agent"] = "planner-agent"
        same_author["records"][0]["spec"]["reviewer"] = "planner-agent"
        same_author["document_id"] = "example/twin-store/1/comment/self-review"
        conflicted = [
            nodes[0],
            nodes[1],
            {"source": "self-review", "body": "", "document": same_author, "last_edited_at": None},
            nodes[3],
        ]
        if not any("must differ" in item for item in validate_log(conflicted, validator)):
            errors.append("self-test: self-approval was accepted")

    graphql_fixture = {
        "data": {
            "repository": {
                "issue": {
                    "body": nodes[0]["body"],
                    "lastEditedAt": None,
                    "author": {"login": "shared-bot"},
                    "comments": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [
                            {
                                "databaseId": 10,
                                "body": nodes[1]["body"],
                                "createdAt": "2026-10-02T13:05:00Z",
                                "lastEditedAt": None,
                                "author": {"login": "shared-bot"},
                            }
                        ],
                    },
                }
            }
        }
    }
    parsed_payload = payload_from_graphql(graphql_fixture)
    if parsed_payload["issue"]["author_login"] != "shared-bot":
        errors.append("self-test: GraphQL author login was not preserved as transport metadata")
    if parsed_payload["comments"][0]["created_at"] != "2026-10-02T13:05:00Z":
        errors.append("self-test: GraphQL comment order fields were not mapped")

    opening_for_link, link_extract_errors = extract_fence(nodes[0]["body"], "body")
    if link_extract_errors or opening_for_link is None:
        errors.extend(link_extract_errors or ["self-test: opening fence missing for link test"])
    else:
        def fake_fetch(url: str, source: str) -> tuple[dict | None, list[str]]:
            if url != "https://example.test/twins/example/twin-store/1/result.json":
                return None, [f"{source}: unexpected Result-Record URL {url}"]
            return opening_for_link, []

        link_nodes = [
            {
                "source": "link-body",
                "body": "Result-Record: https://example.test/twins/example/twin-store/1/result.json\n",
                "last_edited_at": None,
            }
        ]
        errors.extend(validate_log(link_nodes, validator, fetch=fake_fetch))
    insecure = fetch_linked_document("http://example.test/result.json", "insecure-link")[1]
    if not any("must use https" in item for item in insecure):
        errors.append("self-test: non-https Result-Record link was accepted")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"ok: portable bundle, {len(templates)} template documents, "
        f"and the minimal GitHub Issues Twin log validate"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, help="Path to bve-interchange.schema.json")
    parser.add_argument("--self-test", action="store_true", help="Validate in-repo examples and negative cases")
    parser.add_argument("--body", type=Path, help="Issue body markdown")
    parser.add_argument("--comments", type=Path, help="Directory of comment markdown files, sorted by name")
    parser.add_argument("--payload", type=Path, help="JSON payload with issue and comments")
    parser.add_argument("--repository", help="owner/name of a Twin-store repository")
    parser.add_argument("--issue", type=int, help="Issue number to fetch with gh")
    parser.add_argument("--templates", action="store_true", help="Validate profile templates as independent documents")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    schema_path = args.schema or (ROOT / "schemas" / "bve-interchange.schema.json")
    if args.self_test:
        return run_self_test(schema_path)
    try:
        schema = load_schema(schema_path)
        validator = validator_for(schema)
        errors: list[str] = []
        if args.templates:
            errors.extend(_independent_errors(collect_template_documents(), validator))
        if args.body:
            errors.extend(
                validate_log(nodes_from_markdown(args.body, args.comments or Path()), validator)
            )
        if args.payload:
            payload = json.loads(args.payload.read_text(encoding="utf-8"))
            errors.extend(validate_log(nodes_from_payload(payload), validator))
        if args.repository or args.issue:
            if not (args.repository and args.issue):
                errors.append("repository mode requires both --repository and --issue")
            else:
                payload = fetch_repository_issue(args.repository, args.issue)
                errors.extend(validate_log(nodes_from_payload(payload), validator))
        if not any([args.templates, args.body, args.payload, args.repository, args.issue]):
            parser.error("choose --self-test, --body, --payload, --templates, or --repository/--issue")
    except ProfileError as exc:
        print("\n".join(exc.errors), file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
