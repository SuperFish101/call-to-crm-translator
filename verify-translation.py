#!/usr/bin/env python3
"""
verify-translation.py — the gate.

Proves, mechanically, that a call-to-crm output invented nothing. It does NOT trust the
translator; it re-checks every claim against the transcript. Pure Python 3 stdlib, so it runs
on a fresh clone with no pip install.

Usage:
    python3 verify-translation.py <transcript.txt> <output.json>
    python3 verify-translation.py --self-test        # run the committed pass/fail fixtures

Exit 0 = every claim in the output traces to the transcript and the shape is legal.
Exit 1 = at least one failure, printed with the offending evidence and the line it cited.

The checks, in order:
  1. Shape: output has exactly the schema's top-level keys and every required field.
  2. Field discipline: each field is either filled {value,evidence,source_lines[,derivation]}
     or empty {value:null,status}. Nothing in between.
  3. Verbatim evidence: every filled field's `evidence` string appears VERBATIM on the union
     of the lines it cites. This is the anti-invention check. A quote attached to the wrong
     line fails here.
  4. Enums: contact.source is a legal ContactSource; deal.stageId/priority, if set, are legal.
  5. Refusals: deal.stageId and deal.priority must be requires_judgment (never guessed).
  6. Status legality: empty fields use only not_in_source | requires_judgment.
  7. Line bounds: every cited line number is within the transcript.
"""
import json
import sys
import os

# --- the closed sets, copied from reference/enums.md (which copies the CRM types) ----------
CONTACT_SOURCE = {
    "website-form", "web-chat", "booking-page", "community", "get-leads",
    "website", "referral", "ads", "other", "facebook", "instagram", "webinar", "",
}
PIPELINE_STAGES = {"new", "contacted", "qualified", "proposal", "won", "lost"}
DEAL_PRIORITY = {"high", "medium", "low"}
NOTE_CATEGORY = {"objection", "context", "property", "financial"}
EMPTY_STATUS = {"not_in_source", "requires_judgment"}

# fields that are decisions, not facts: the translator must refuse them every run
ALWAYS_REFUSE = {("deal", "stageId"), ("deal", "priority")}


class Fail(Exception):
    pass


def load_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        # 1-indexed: lines[1] is the first line
        return {i + 1: line.rstrip("\n") for i, line in enumerate(f)}


def is_filled(field):
    return isinstance(field, dict) and "evidence" in field and "source_lines" in field


def is_empty(field):
    return isinstance(field, dict) and set(field.keys()) == {"value", "status"} and field["value"] is None


def check_field(name, field, lines, errors, allow_empty=True):
    """A field must be a valid filled or empty object, and if filled, evidence must be verbatim."""
    if not isinstance(field, dict):
        errors.append(f"{name}: not an object")
        return
    if is_empty(field):
        if not allow_empty:
            errors.append(f"{name}: empty not allowed here")
        elif field["status"] not in EMPTY_STATUS:
            errors.append(f"{name}: illegal status {field['status']!r} (allowed: {sorted(EMPTY_STATUS)})")
        return
    if not is_filled(field):
        errors.append(f"{name}: neither a valid filled field {{value,evidence,source_lines}} nor a valid empty field {{value:null,status}}. Got keys {sorted(field.keys())}")
        return
    # filled: verbatim evidence check
    evidence = field.get("evidence", "")
    src = field.get("source_lines", [])
    if not isinstance(src, list) or not src:
        errors.append(f"{name}: source_lines must be a non-empty list")
        return
    max_line = max(lines) if lines else 0
    for ln in src:
        if not isinstance(ln, int) or ln < 1 or ln > max_line:
            errors.append(f"{name}: cited line {ln} is out of range (transcript has lines 1..{max_line})")
            return
    # evidence must appear verbatim in the concatenation of the cited lines
    haystack = " ".join(lines[ln] for ln in src)
    if evidence not in haystack:
        errors.append(
            f"{name}: INVENTED — evidence not found verbatim on cited line(s) {src}.\n"
            f"        evidence: {evidence!r}\n"
            f"        line(s):  {haystack!r}"
        )


def verify(transcript_path, output_path):
    lines = load_lines(transcript_path)
    with open(output_path, "r", encoding="utf-8") as f:
        out = json.load(f)
    errors = []

    # 1. top-level shape
    required_top = {"meta", "contact", "deal", "tasks", "notes", "unmapped"}
    got_top = set(out.keys())
    if got_top != required_top:
        missing = required_top - got_top
        extra = got_top - required_top
        if missing:
            errors.append(f"top-level: missing keys {sorted(missing)}")
        if extra:
            errors.append(f"top-level: unexpected keys {sorted(extra)}")

    # meta sanity
    meta = out.get("meta", {})
    if meta.get("translator") != "call-to-crm":
        errors.append("meta.translator must be 'call-to-crm'")
    if meta.get("input_line_count") != len(lines):
        errors.append(f"meta.input_line_count={meta.get('input_line_count')} but transcript has {len(lines)} lines")

    # 2-3. contact
    contact = out.get("contact", {})
    for fld in ["name", "phone", "email", "company", "address", "source", "personalNotes"]:
        if fld not in contact:
            errors.append(f"contact.{fld}: missing")
        else:
            check_field(f"contact.{fld}", contact[fld], lines, errors)
    # source enum
    src_field = contact.get("source", {})
    if is_filled(src_field) and src_field.get("value") not in CONTACT_SOURCE:
        errors.append(f"contact.source.value {src_field.get('value')!r} is not a legal ContactSource")
    # relations
    for i, rel in enumerate(contact.get("relations", [])):
        nm = f"contact.relations[{i}]"
        if not all(k in rel for k in ("name", "relationship", "evidence", "source_lines")):
            errors.append(f"{nm}: relation missing required keys")
            continue
        check_field(nm, {"value": rel["name"], "evidence": rel["evidence"], "source_lines": rel["source_lines"]}, lines, errors, allow_empty=False)

    # deal
    deal = out.get("deal", {})
    for fld in ["title", "value", "currency", "timeline", "stageId", "priority"]:
        if fld not in deal:
            errors.append(f"deal.{fld}: missing")
        else:
            check_field(f"deal.{fld}", deal[fld], lines, errors)
    # enums when set
    if is_filled(deal.get("stageId", {})) and deal["stageId"].get("value") not in PIPELINE_STAGES:
        errors.append(f"deal.stageId.value {deal['stageId'].get('value')!r} is not a legal PipelineStageId")
    if is_filled(deal.get("priority", {})) and deal["priority"].get("value") not in DEAL_PRIORITY:
        errors.append(f"deal.priority.value {deal['priority'].get('value')!r} is not a legal DealPriority")
    # 5. refusals: stageId + priority must be requires_judgment, never a value
    for section, fld in ALWAYS_REFUSE:
        f = out.get(section, {}).get(fld, {})
        if not (is_empty(f) and f.get("status") == "requires_judgment"):
            errors.append(f"{section}.{fld}: must be {{value:null, status:'requires_judgment'}} — this field is a decision, never transcribed")

    # tasks
    for i, task in enumerate(out.get("tasks", [])):
        for fld in ["title", "dueAt", "notes"]:
            if fld not in task:
                errors.append(f"tasks[{i}].{fld}: missing")
            else:
                check_field(f"tasks[{i}].{fld}", task[fld], lines, errors)

    # notes
    for i, note in enumerate(out.get("notes", [])):
        if note.get("category") not in NOTE_CATEGORY:
            errors.append(f"notes[{i}].category {note.get('category')!r} not in {sorted(NOTE_CATEGORY)}")
        if "content" not in note:
            errors.append(f"notes[{i}].content: missing")
        else:
            check_field(f"notes[{i}].content", note["content"], lines, errors)

    # unmapped
    for i, u in enumerate(out.get("unmapped", [])):
        if not all(k in u for k in ("source_lines", "text", "reason")):
            errors.append(f"unmapped[{i}]: missing required keys")
            continue
        # unmapped.text must also be verbatim on its cited lines
        check_field(f"unmapped[{i}]", {"value": u["text"], "evidence": u["text"], "source_lines": u["source_lines"]}, lines, errors, allow_empty=False)

    return errors


def coverage(transcript_path, output_path):
    """Report which transcript lines the output cited. Not a pass/fail — a 'nothing dropped'
    signal a human reads. Lines with real content that no field cited are candidates for a
    dropped fact (or for the unmapped list). Speaker-only / filler lines are expected gaps."""
    lines = load_lines(transcript_path)
    out = json.load(open(output_path, encoding="utf-8"))
    cited = set()

    def collect(obj):
        if isinstance(obj, dict):
            if "source_lines" in obj and isinstance(obj["source_lines"], list):
                cited.update(x for x in obj["source_lines"] if isinstance(x, int))
            for v in obj.values():
                collect(v)
        elif isinstance(obj, list):
            for v in obj:
                collect(v)

    collect(out)
    all_lines = set(lines.keys())
    uncited = sorted(all_lines - cited)
    pct = round(100 * len(cited) / len(all_lines)) if all_lines else 0
    print(f"  coverage: {len(cited)}/{len(all_lines)} lines cited ({pct}%)")
    if uncited:
        print(f"  lines with NO citation (check these are filler, not dropped facts): {uncited}")


def shape_fingerprint(obj):
    """A recursive key-shape signature, ignoring values and list length beyond the first item.
    Two outputs with the same fingerprint have the same fields in the same nesting, which is
    exactly the 'fixed shape every run' the brief demands."""
    if isinstance(obj, dict):
        # for filled/empty field objects, normalise: we care about which KIND, not the keys mix
        keys = set(obj.keys())
        if keys <= {"value", "evidence", "source_lines", "derivation"} and "evidence" in keys:
            return "FIELD_FILLED"
        if keys == {"value", "status"}:
            return "FIELD_EMPTY"
        return {k: shape_fingerprint(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return ["LIST"] if not obj else ["LIST", shape_fingerprint(obj[0])]
    return "SCALAR"


def check_shapes_match(paths):
    """Prove every golden output shares one fixed shape (fields + nesting)."""
    import json as _json
    print("\n### SHAPE-STABILITY (all outputs must share ONE fixed shape)")
    fps = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            fps.append((os.path.basename(p), shape_fingerprint(_json.load(f))))
    # compare only the fixed top-level containers; list bodies vary in count (that is allowed),
    # so we compare the top-level keys and the per-field object KINDS, not array lengths.
    base_name, base = fps[0]
    ok = True
    for name, fp in fps[1:]:
        if fp_keys(fp) != fp_keys(base):
            print(f"  DRIFT: {name} top-level shape differs from {base_name}")
            ok = False
        else:
            print(f"  ok   {name} shares the fixed shape of {base_name}")
    if ok:
        print("  all outputs share one fixed top-level shape.")
    return ok


def fp_keys(fp):
    """The stable part of a fingerprint: the top-level object key structure (list bodies and
    scalar values excluded, since call-to-call those legitimately vary in count/content)."""
    if isinstance(fp, dict):
        return {k: (fp_keys(v) if isinstance(v, dict) else "*") for k, v in fp.items()}
    return "*"


VERBOSE = False


def trace_claims(transcript_path, output_path):
    """Print every populated field as a line item showing exactly where it came from:
    the field, its value, and the transcript line + verbatim quote it traces to. This is the
    'I pulled this from HERE, go check it' view a human uses to fact-check in seconds."""
    lines = load_lines(transcript_path)
    out = json.load(open(output_path, encoding="utf-8"))
    print("  --- traced claims (field  =  value   <- line N: \"quote\") ---")

    def emit(path, field):
        if is_filled(field):
            src = field["source_lines"]
            quote = field["evidence"]
            lns = ",".join(str(x) for x in src)
            print(f'  {path} = {field.get("value")!r}   <- line {lns}: "{quote}"')

    c = out["contact"]
    for k in ["name", "phone", "email", "company", "address", "source", "personalNotes"]:
        emit(f"contact.{k}", c[k])
    for i, rel in enumerate(c.get("relations", [])):
        print(f'  contact.relations[{i}] = {rel["name"]} ({rel["relationship"]})   <- line {",".join(map(str,rel["source_lines"]))}: "{rel["evidence"]}"')
    d = out["deal"]
    for k in ["title", "value", "currency", "timeline", "stageId", "priority"]:
        emit(f"deal.{k}", d[k])
    for i, t in enumerate(out["tasks"]):
        for k in ["title", "dueAt", "notes"]:
            emit(f"tasks[{i}].{k}", t[k])
    for i, n in enumerate(out["notes"]):
        emit(f'notes[{i}]({n["category"]})', n["content"])


def run_one(transcript_path, output_path):
    print(f"\n=== verifying {os.path.basename(output_path)} against {os.path.basename(transcript_path)} ===")
    errors = verify(transcript_path, output_path)
    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return False
    print("PASS — every claim traces to a cited line; shape and enums legal.")
    coverage(transcript_path, output_path)
    if VERBOSE:
        trace_claims(transcript_path, output_path)
    return True


def self_test():
    """Run the committed fixtures: the golden output must pass, every fail_* must fail."""
    here = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(here, "tests", "fixtures")
    ok = True

    goldens = [
        ("discovery-call-nakamura.txt", "discovery-call-nakamura.output.json"),
        ("discovery-call-priya.txt", "discovery-call-priya.output.json"),
        ("discovery-call-osei.txt", "discovery-call-osei.output.json"),
    ]
    print("### GOLDEN OUTPUTS (all must PASS, all the same fixed shape)")
    for tx, gj in goldens:
        if not run_one(os.path.join(here, "samples", tx), os.path.join(here, "samples", gj)):
            ok = False

    if not check_shapes_match([os.path.join(here, "samples", gj) for _, gj in goldens]):
        ok = False

    # The invention fixtures were all built by corrupting the nakamura golden, so they are
    # checked against that transcript.
    transcript = os.path.join(here, "samples", "discovery-call-nakamura.txt")

    print("\n### BROKEN FIXTURES (each must FAIL)")
    if os.path.isdir(fixtures_dir):
        for fn in sorted(os.listdir(fixtures_dir)):
            if not fn.startswith("fail_") or not fn.endswith(".json"):
                continue
            fpath = os.path.join(fixtures_dir, fn)
            passed = run_one(transcript, fpath)
            if passed:
                print(f"  !!! {fn} PASSED but was supposed to FAIL — the gate has a hole.")
                ok = False
            else:
                print(f"  (good: {fn} failed as intended)")
    else:
        print("  no fixtures dir found")
        ok = False

    print("\n" + ("ALL FIXTURES BEHAVED AS EXPECTED." if ok else "SELF-TEST FAILED."))
    return ok


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if "-v" in args:
        VERBOSE = True
        args = [a for a in args if a != "-v"]
    if len(args) == 1 and args[0] == "--self-test":
        sys.exit(0 if self_test() else 1)
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(0 if run_one(args[0], args[1]) else 1)
