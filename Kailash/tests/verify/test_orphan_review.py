"""Orphan review tests: accountability by label, and the removal gate.

Two guarantees carry the weight here. First, Property 14: the review exits 0
iff every observed container is compose-owned (by the config-files label, not
by name) or validly retained, and every unaccounted container is printed with
its name and image. Second, Property 15: `docker rm` is never issued without
explicit per-run confirmation naming exactly the remove-dispositioned set --
verified with the recording executor, no daemon, nothing removed.

The classifier is pure, so every disposition shape runs from synthetic
container lists. The collector tests assert the exact commands issued: all of
them read-only, and none of them capturing `.Config.Env`, because the compose
environment carries credential values the evidence file must never embed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import orphan_review as orv
from scripts.verify.common import Exit, Unavailable, Usage

from .conftest import REPO_ROOT, FakeExecutor

TRACKED = "C:\\repo\\docker-compose.yml"
PS_CMD = "docker ps -a --no-trunc --format {{.Names}}\t{{.Image}}\t{{.ID}}\t{{.Status}}"

# The six containers Requirement 7.1 names. The check itself never hardcodes
# them -- the model is general -- but the shipped artifact must classify each.
SIX = ("mcp-tunnel-cloudflared-1", "mcp-tunnel-mcp-proxy-1", "log-reader",
       "nervous_dhawan", "interesting_northcutt", "gifted_leavitt")


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

def container(name, image="img:latest", *, config_files="", ports=None,
              present=True, parse_errors=None):
    """One evidence-shaped container, as the collector would have written it."""
    return {
        "name": name, "image": image, "container_id": f"cid-{name}",
        "ps_status": "Up 2 hours", "created": "2026-07-28T20:05:12Z",
        "state_status": "running", "started_at": "2026-07-31T11:58:18Z",
        "labels": {}, "compose_project": "", "compose_service": "",
        "compose_config_files": config_files,
        "published_ports": list(ports or []),
        "command": "sleep infinity", "present": present,
        "capture_failed": [], "parse_errors": dict(parse_errors or {}),
    }


def evidence(*containers, compose_files=(TRACKED,)):
    return {"captured_at": "2026-08-01T00:00:00+00:00",
            "compose_files": list(compose_files),
            "containers": list(containers)}


def retained_entry(name, image="img:latest", *, owner="docs/records/x.md -- reviewed",
                   ports=(), justification="reviewed and kept", reviewed="2026-08-01"):
    return {"name": name, "image": image, "owner": owner,
            "published_ports": list(ports), "justification": justification,
            "reviewed": reviewed}


def removal_entry(name, image="img:latest", *, reason="ad-hoc leftover",
                  reviewed="2026-08-01"):
    return {"name": name, "image": image, "reason": reason, "reviewed": reviewed}


def doc(retained=(), removals=()):
    return orv.read_retained_doc({"retained": list(retained),
                                  "proposed_removals": list(removals)})


def ns(root, *, retained, execute, execute_removals=None, yes=False,
       from_evidence=None, evidence_path=None, emit_record=None):
    return argparse.Namespace(
        root=root, json=False, emit_record=emit_record, retained=retained,
        evidence=evidence_path, from_evidence=from_evidence,
        execute_removals=execute_removals, yes=yes, execute=execute)


def script_host(fake, containers: dict):
    """Script `docker ps` plus the per-container captures the tests care about.

    Unscripted inspects return exit 0 with empty stdout, which the collector
    records as an empty capture -- so only labels, image and ports need
    scripting here.
    """
    roster = "\n".join(f"{n}\t{c.get('image', 'img:latest')}\tcid-{n}\tUp 2 hours"
                       for n, c in containers.items())
    fake.script(PS_CMD, 0, roster + "\n")
    for n, c in containers.items():
        fake.script(f"docker inspect --format {{{{json .Config.Labels}}}} {n}",
                    0, json.dumps(c.get("labels", {})))
        fake.script(f"docker inspect --format {{{{.Config.Image}}}} {n}",
                    0, c.get("image", "img:latest") + "\n")
        fake.script(f"docker inspect --format {{{{json .NetworkSettings.Ports}}}} {n}",
                    0, json.dumps(c.get("ports", {})))


def write_json(path: Path, obj) -> Path:
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Collector: read-only, and never the environment
# --------------------------------------------------------------------------

def test_collector_issues_only_read_commands_and_never_captures_env(tmp_repo, fake_executor):
    tmp_repo.write("docker-compose.yml", "services: {}\n")
    script_host(fake_executor, {"alpha": {}, "beta": {}})

    ev = orv.collect(tmp_repo.root, fake_executor)

    cmds = fake_executor.commands()
    assert cmds
    assert all(c.startswith(("docker version", "docker ps", "docker inspect"))
               for c in cmds)
    for fragment in ("docker rm", "docker stop", "docker update", "docker kill"):
        fake_executor.assert_never(fragment)
    # `.Config.Env` (credentials) and the whole-config dump that would include
    # it must never be captured into the evidence file.
    assert all(".Config.Env" not in c and "{{json .Config}}" not in c for c in cmds)
    assert [c["name"] for c in ev["containers"]] == ["alpha", "beta"]


def test_collector_captures_the_named_evidence_fields(tmp_repo, fake_executor):
    tmp_repo.write("docker-compose.yml", "services: {}\n")
    script_host(fake_executor, {"alpha": {
        "image": "img-a:1",
        "labels": {orv.CONFIG_FILES_LABEL: "C:\\elsewhere\\docker-compose.yml",
                   orv.PROJECT_LABEL: "other-project"},
        "ports": {"80/tcp": [{"HostIp": "127.0.0.1", "HostPort": "3000"}],
                  "5432/tcp": None},
    }})
    fake_executor.script("docker inspect --format {{.Created}} alpha",
                         0, "2026-07-28T20:05:12Z\n")
    fake_executor.script("docker inspect --format {{json .Config.Entrypoint}} alpha",
                         0, '["tail"]')
    fake_executor.script("docker inspect --format {{json .Config.Cmd}} alpha",
                         0, '["-f", "/dev/null"]')

    ev = orv.collect(tmp_repo.root, fake_executor)

    c = ev["containers"][0]
    assert c["image"] == "img-a:1"
    assert c["compose_project"] == "other-project"
    assert c["compose_config_files"] == "C:\\elsewhere\\docker-compose.yml"
    # Only the published binding survives; the exposed-but-unpublished port is
    # not listening on the host and is not 7.5 evidence.
    assert c["published_ports"] == [
        {"host_ip": "127.0.0.1", "host_port": "3000", "container_port": "80/tcp"}]
    assert c["command"] == "tail -f /dev/null"
    assert c["created"] == "2026-07-28T20:05:12Z"
    assert ev["compose_files"] == [str(tmp_repo.root / "docker-compose.yml")]


def test_unreachable_daemon_is_unavailable_not_a_pass(tmp_repo, fake_executor):
    fake_executor.script("docker version --format {{json .}}", 1, "",
                         "error during connect: docker daemon is not running")
    with pytest.raises(Unavailable):
        orv.collect(tmp_repo.root, fake_executor)


# --------------------------------------------------------------------------
# Classifier: ownership is the label, not the name
# --------------------------------------------------------------------------

def test_compose_ownership_is_by_label_and_survives_windows_spelling():
    ev = evidence(
        container("backend", config_files="c:/REPO/docker-compose.yml"),
        container("worker",
                  config_files="C:\\other\\x.yml,C:\\repo\\docker-compose.yml"),
        compose_files=("C:\\repo\\docker-compose.yml",))
    findings, assessments, _ = orv.classify(ev, doc())
    assert findings == []
    assert [a.disposition for a in assessments] == [orv.COMPOSE_OWNED] * 2


def test_a_kailash_name_from_a_foreign_compose_file_is_not_accounted():
    """Names are cosmetic: a container named like the stack's backend, started
    from an untracked compose file, is not the stack's backend."""
    ev = evidence(container("kailash-backend", image="img:x",
                            config_files="C:\\stranger\\docker-compose.yml"))
    findings, assessments, _ = orv.classify(ev, doc())
    assert [f.rule for f in findings] == ["unaccounted-container"]
    assert assessments[0].disposition == orv.UNACCOUNTED


def test_a_valid_retained_entry_accounts_for_its_container():
    findings, assessments, _ = orv.classify(
        evidence(container("keeper")), doc(retained=[retained_entry("keeper")]))
    assert findings == []
    assert assessments[0].disposition == orv.RETAINED
    assert assessments[0].owner == "docs/records/x.md -- reviewed"


def test_unaccounted_container_is_printed_with_name_and_image():
    findings, _, _ = orv.classify(
        evidence(container("stray", image="mystery:9")), doc())
    rendered = findings[0].render()
    assert "stray" in rendered
    assert "mystery:9" in rendered


def test_retained_entry_with_empty_owner_is_dropped_and_container_reappears():
    d = doc(retained=[retained_entry("keeper", owner="  ")])
    findings, _, _ = orv.classify(evidence(container("keeper")), d)
    assert sorted(f.rule for f in findings) == \
        ["retained-entry-invalid", "unaccounted-container"]


def test_unparseable_retained_file_is_a_finding_not_a_skip(tmp_path):
    path = write_json(tmp_path / "retained.json", None)
    path.write_text("{not json", encoding="utf-8")
    d, notes = orv.load_retained(path)
    assert notes == []
    assert [f.rule for f in d.findings] == ["retained-list-unparseable"]
    assert d.retained == {}
    assert d.removals == {}


def test_missing_retained_file_retains_nothing_and_says_so(tmp_path):
    d, notes = orv.load_retained(tmp_path / "absent.json")
    assert d.retained == {}
    assert d.findings == ()
    assert any("nothing is retained" in n for n in notes)


def test_retained_published_port_must_be_recorded_with_bind_address():
    port = {"host_ip": "127.0.0.1", "host_port": "8812", "container_port": "8812/tcp"}
    observed = container("keeper", ports=[port])

    findings, _, _ = orv.classify(evidence(observed),
                                  doc(retained=[retained_entry("keeper")]))
    assert [f.rule for f in findings] == ["retained-port-unrecorded"]
    assert "127.0.0.1:8812" in findings[0].render()

    findings, _, _ = orv.classify(
        evidence(observed), doc(retained=[retained_entry("keeper", ports=[port])]))
    assert findings == []


def test_retained_image_mismatch_is_a_finding():
    d = doc(retained=[retained_entry("keeper", image="img:reviewed")])
    findings, _, _ = orv.classify(evidence(container("keeper", image="img:other")), d)
    assert [f.rule for f in findings] == ["retained-image-mismatch"]


def test_a_recorded_remove_disposition_is_still_a_finding_until_executed():
    d = doc(removals=[removal_entry("victim", image="img:v")])
    findings, assessments, _ = orv.classify(
        evidence(container("victim", image="img:v")), d)
    assert [f.rule for f in findings] == ["removal-pending"]
    rendered = findings[0].render()
    assert "victim" in rendered
    assert "img:v" in rendered
    assert assessments[0].disposition == orv.REMOVE_PROPOSED


def test_both_dispositions_for_one_name_is_a_conflict_and_neither_applies():
    d = doc(retained=[retained_entry("dual")], removals=[removal_entry("dual")])
    assert [f.rule for f in d.findings] == ["disposition-conflict"]
    findings, _, _ = orv.classify(evidence(container("dual")), d)
    assert sorted(f.rule for f in findings) == \
        ["disposition-conflict", "unaccounted-container"]


def test_a_container_that_vanished_mid_capture_is_noted_not_failed():
    findings, assessments, notes = orv.classify(
        evidence(container("gone", present=False)), doc())
    assert findings == []
    assert assessments[0].disposition == orv.ABSENT
    assert any("gone" in n for n in notes)


def test_stale_entries_are_notes_not_findings():
    d = doc(retained=[retained_entry("departed")],
            removals=[removal_entry("already-gone")])
    findings, _, notes = orv.classify(evidence(), d)
    assert findings == []
    assert any("departed" in n for n in notes)
    assert any("already-gone" in n for n in notes)


POOL = ("c-one", "c-two", "c-three", "c-four", "c-five")


# Feature: production-readiness, Property 14: For any set of containers
# observed on the Docker_Host, the orphan review exits 0 if and only if every
# observed container is either a service of the tracked Compose_Stack or
# validly listed as retained; every unaccounted container is printed with its
# name and image; and every retained entry carries a non-empty owner.
@given(assignment=st.dictionaries(
    st.sampled_from(POOL),
    st.sampled_from(["compose", "retained", "retained-broken", "remove",
                     "unaccounted"]),
    max_size=len(POOL)))
def test_property_14_every_container_is_accounted_for(assignment):
    containers, retained, removals = [], [], []
    for name, kind in sorted(assignment.items()):
        image = f"img-{name}:1"
        if kind == "compose":
            containers.append(container(name, image=image, config_files=TRACKED))
        elif kind == "retained":
            containers.append(container(name, image=image))
            retained.append(retained_entry(name, image=image))
        elif kind == "retained-broken":
            containers.append(container(name, image=image))
            retained.append(retained_entry(name, image=image, owner=""))
        elif kind == "remove":
            containers.append(container(name, image=image))
            removals.append(removal_entry(name, image=image))
        else:
            containers.append(container(name, image=image))

    d = orv.read_retained_doc({"retained": retained, "proposed_removals": removals})
    findings, _, _ = orv.classify(evidence(*containers), d)

    accounted = all(kind in ("compose", "retained") for kind in assignment.values())
    assert (not findings) == accounted
    rendered = "\n".join(f.render() for f in findings)
    for name, kind in assignment.items():
        if kind in ("unaccounted", "retained-broken", "remove"):
            assert name in rendered
            assert f"img-{name}:1" in rendered


# --------------------------------------------------------------------------
# The removal gate (Requirement 7.3, Property 15)
# --------------------------------------------------------------------------

def test_remove_without_confirmation_returns_empty_and_issues_nothing(fake_executor):
    assert orv.remove(["a", "b"], confirmed=False, execute=fake_executor) == []
    fake_executor.assert_never("docker rm")
    assert fake_executor.commands() == []


def test_remove_with_confirmation_issues_docker_rm_for_exactly_the_set(fake_executor):
    orv.remove(["a", "b"], confirmed=True, execute=fake_executor)
    assert fake_executor.matching("docker rm") == ["docker rm -f a", "docker rm -f b"]
    assert {c.argv[-1] for c in fake_executor.calls} == {"a", "b"}


# Feature: production-readiness, Property 15: For any set of container removal
# candidates, no destructive command is issued unless explicit operator
# confirmation is present for that specific set.
@given(candidates=st.sets(st.sampled_from(POOL), max_size=len(POOL)),
       named=st.sets(st.sampled_from(POOL), max_size=len(POOL)),
       confirmed=st.booleans())
def test_property_15_no_removal_without_confirmation_of_that_set(
        candidates, named, confirmed):
    fake = FakeExecutor()
    ok, _ = orv.removal_gate(named, candidates, confirmed=confirmed)
    assert ok == (confirmed and bool(named) and named == candidates)

    orv.remove(sorted(candidates), confirmed=ok, execute=fake)

    issued = fake.matching("docker rm")
    if not ok:
        assert issued == []
    else:
        # Set equality in both directions: everything confirmed is removed,
        # and nothing outside the confirmed set ever reaches an argv.
        assert set(issued) == {f"docker rm -f {name}" for name in candidates}
        assert {c.argv[-1] for c in fake.calls} == candidates


# ---- the CLI path, end to end with the recording executor ------------------

def _cli_host(tmp_repo, fake_executor, tmp_path):
    """A host with one compose-owned container, one retained, one stray and
    two recorded removal candidates, plus the retained file recording them."""
    tmp_repo.write("docker-compose.yml", "services: {}\n")
    owned_label = {orv.CONFIG_FILES_LABEL: str(tmp_repo.root / "docker-compose.yml")}
    script_host(fake_executor, {
        "kailash-backend": {"labels": owned_label},
        "keeper": {},
        "stray": {},
        "victim-one": {},
        "victim-two": {},
    })
    retained = write_json(tmp_path / "retained.json", {
        "retained": [retained_entry("keeper")],
        "proposed_removals": [removal_entry("victim-one"),
                              removal_entry("victim-two")],
    })
    return retained


def test_confirmed_removal_issues_exactly_the_named_set(tmp_repo, fake_executor, tmp_path):
    tmp_repo.write("docker-compose.yml", "services: {}\n")
    owned_label = {orv.CONFIG_FILES_LABEL: str(tmp_repo.root / "docker-compose.yml")}
    script_host(fake_executor, {
        "kailash-backend": {"labels": owned_label},
        "victim-one": {},
        "victim-two": {},
    })
    retained = write_json(tmp_path / "retained.json", {
        "retained": [],
        "proposed_removals": [removal_entry("victim-one"),
                              removal_entry("victim-two")],
    })

    report = orv.build_report(ns(
        tmp_repo.root, retained=retained, execute=fake_executor,
        execute_removals=["victim-two", "victim-one"], yes=True))

    assert set(fake_executor.matching("docker rm")) == {
        "docker rm -f victim-one", "docker rm -f victim-two"}
    assert any("removed victim-one" in n for n in report.notes)
    # The pending findings are cleared by the successful removal, so the run
    # ends green: the host now shows only compose-owned containers.
    assert report.exit_code() == Exit.OK


@pytest.mark.parametrize("named,yes", [
    (["victim-one", "victim-two"], False),           # the set, but no --yes
    (["victim-one"], True),                          # a recorded candidate unnamed
    (["victim-one", "victim-two", "keeper"], True),  # a retained container named
    (["victim-one", "victim-two", "stray"], True),   # an undispositioned named
    (["victim-one", "victim-two", "ghost"], True),   # a container not observed
])
def test_refused_removals_issue_no_docker_rm(tmp_repo, fake_executor, tmp_path,
                                             named, yes):
    retained = _cli_host(tmp_repo, fake_executor, tmp_path)

    with pytest.raises(Usage):
        orv.build_report(ns(tmp_repo.root, retained=retained,
                            execute=fake_executor,
                            execute_removals=named, yes=yes))

    fake_executor.assert_never("docker rm")
    fake_executor.assert_never("docker stop")


def test_retained_and_undispositioned_names_never_reach_a_rm_argv(
        tmp_repo, fake_executor, tmp_path):
    """Even on a run that does remove, `keeper` and `stray` appear in no
    `docker rm` argv -- the gate filters by disposition, not by presence."""
    retained = _cli_host(tmp_repo, fake_executor, tmp_path)

    report = orv.build_report(ns(
        tmp_repo.root, retained=retained, execute=fake_executor,
        execute_removals=["victim-one", "victim-two"], yes=True))

    rm_argvs = [c.argv for c in fake_executor.calls if "rm" in c.argv[:2]]
    assert {argv[-1] for argv in rm_argvs} == {"victim-one", "victim-two"}
    assert all("keeper" not in argv and "stray" not in argv for argv in rm_argvs)
    # `stray` is still unaccounted, so the run stays red even after removal.
    assert [f.rule for f in report.findings] == ["unaccounted-container"]


def test_yes_alone_confirms_nothing(tmp_repo, fake_executor, tmp_path):
    retained = write_json(tmp_path / "retained.json", {"retained": []})
    with pytest.raises(Usage):
        orv.build_report(ns(tmp_repo.root, retained=retained,
                            execute=fake_executor, yes=True))
    assert fake_executor.commands() == []


def test_removals_from_recorded_evidence_are_refused(tmp_repo, fake_executor, tmp_path):
    """A recorded capture may be older than the host; only a live run can
    confirm what would be removed."""
    ev = write_json(tmp_path / "ev.json", evidence(container("victim-one")))
    retained = write_json(tmp_path / "retained.json",
                          {"retained": [],
                           "proposed_removals": [removal_entry("victim-one")]})
    with pytest.raises(Usage):
        orv.build_report(ns(tmp_repo.root, retained=retained,
                            execute=fake_executor, from_evidence=ev,
                            execute_removals=["victim-one"], yes=True))
    assert fake_executor.commands() == []


def test_from_evidence_classifies_without_contacting_docker(tmp_repo, fake_executor,
                                                            tmp_path):
    ev = write_json(tmp_path / "ev.json", evidence(container("stray", image="img:s")))
    retained = write_json(tmp_path / "retained.json", {"retained": []})

    report = orv.build_report(ns(tmp_repo.root, retained=retained,
                                 execute=fake_executor, from_evidence=ev))

    assert report.exit_code() == Exit.FAILED
    assert fake_executor.commands() == []


# --------------------------------------------------------------------------
# The generated record
# --------------------------------------------------------------------------

def test_record_is_generated_from_the_retained_list_and_the_observation():
    port = {"host_ip": "127.0.0.1", "host_port": "8812", "container_port": "8812/tcp"}
    d = doc(retained=[retained_entry("keeper", image="img:k",
                                     owner="docs/guides/x.md -- tunnel",
                                     ports=[port])],
            removals=[removal_entry("victim", image="img:v",
                                    reason="leftover ad-hoc run")])
    _, assessments, _ = orv.classify(evidence(
        container("owned", config_files=TRACKED),
        container("keeper", image="img:k", ports=[port]),
        container("victim", image="img:v"),
        container("stray", image="img:s")), d)

    record = orv.render_record(d, assessments,
                               captured_at="2026-08-01T00:00:00+00:00")

    assert "### keeper" in record
    assert "docs/guides/x.md -- tunnel" in record
    assert "127.0.0.1:8812 -> 8812/tcp" in record
    assert "### victim" in record
    assert "leftover ad-hoc run" in record
    assert "`stray` -- image `img:s`" in record
    assert "- `owned`" in record


# --------------------------------------------------------------------------
# The shipped artifact: the six named containers, and the schema agreement
# --------------------------------------------------------------------------

def _shipped(rel: str):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def test_shipped_retained_list_is_valid_and_classifies_all_six():
    d = orv.read_retained_doc(_shipped(orv.RETAINED_PATH))
    assert d.findings == ()
    assert set(d.retained) | set(d.removals) == set(SIX)
    for entry in d.retained.values():
        assert entry["owner"].strip()
    for entry in d.removals.values():
        assert entry["reason"].strip()


def test_schema_file_and_validator_require_the_same_keys():
    """One schema, stated twice on purpose -- and held identical here, so the
    JSON Schema cannot drift from what the module actually enforces."""
    defs = _shipped(orv.SCHEMA_PATH)["$defs"]
    assert tuple(defs["retained_entry"]["required"]) == orv.REQUIRED_RETAINED_KEYS
    assert tuple(defs["removal_entry"]["required"]) == orv.REQUIRED_REMOVAL_KEYS
    assert tuple(defs["published_port"]["required"]) == orv.REQUIRED_PORT_KEYS


def test_shipped_retained_list_matches_its_json_schema():
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(_shipped(orv.RETAINED_PATH), _shipped(orv.SCHEMA_PATH))


def test_artifacts_embed_no_denylisted_literal():
    """The review artifacts carry labels and ports, never container env --
    which is where the compose credential fallbacks would leak from."""
    denylist = [line.strip() for line in
                (REPO_ROOT / "scripts/verify/data/denylist.txt")
                .read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")]
    assert denylist
    for rel in (orv.RETAINED_PATH, orv.SCHEMA_PATH, orv.RECORD_PATH,
                orv.EVIDENCE_PATH):
        path = REPO_ROOT / rel
        if not path.is_file():
            continue  # the generated records exist only after a live run
        text = path.read_text(encoding="utf-8")
        for literal in denylist:
            assert literal not in text, f"{literal!r} found in {rel}"
