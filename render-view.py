#!/usr/bin/env python3
"""
render-view.py — turn a call-to-crm JSON output into a human-readable markdown CRM card.

Every filled field renders with its source citation inline, so a reader sees the value AND
exactly where it came from without opening the JSON:

    **Name:** Trevor Nakamura  _(line 2: "it's Trevor Nakamura")_

Empty fields render their status so a reader sees the tool refused or found nothing, rather
than a silent blank.

Usage:  python3 render-view.py <output.json>   > record.md
Pure Python 3 stdlib.
"""
import json
import sys


def cite(field):
    if field.get("value") is None:
        status = field.get("status", "empty")
        tag = {"not_in_source": "not in source", "requires_judgment": "requires human judgment"}.get(status, status)
        return f"_{tag}_"
    lns = ",".join(str(x) for x in field["source_lines"])
    return f'{field["value"]}  _(line {lns}: "{field["evidence"]}")_'


def main(path):
    out = json.load(open(path, encoding="utf-8"))
    L = []
    m = out["meta"]
    L.append(f"# CRM record from {m['input_file']}")
    L.append("")
    L.append(f"_Translated by {m['translator']} v{m['version']} from a {m['input_line_count']}-line transcript. "
             f"Every value below cites the transcript line it came from. Empty fields say why._")
    L.append("")
    if m.get("assumptions"):
        L.append("**Declared assumptions (not from the call):**")
        for a in m["assumptions"]:
            L.append(f"- {a}")
        L.append("")

    c = out["contact"]
    L.append("## Contact")
    L.append(f"- **Name:** {cite(c['name'])}")
    L.append(f"- **Phone:** {cite(c['phone'])}")
    L.append(f"- **Email:** {cite(c['email'])}")
    L.append(f"- **Company:** {cite(c['company'])}")
    L.append(f"- **Address:** {cite(c['address'])}")
    L.append(f"- **Source:** {cite(c['source'])}")
    L.append(f"- **Personal notes:** {cite(c['personalNotes'])}")
    if c.get("relations"):
        L.append("- **Relations:**")
        for r in c["relations"]:
            lns = ",".join(str(x) for x in r["source_lines"])
            L.append(f'  - {r["name"]} ({r["relationship"]})  _(line {lns}: "{r["evidence"]}")_')
    L.append("")

    d = out["deal"]
    L.append("## Deal")
    L.append(f"- **Title:** {cite(d['title'])}")
    L.append(f"- **Value:** {cite(d['value'])}")
    L.append(f"- **Currency:** {cite(d['currency'])}")
    L.append(f"- **Timeline:** {cite(d['timeline'])}")
    L.append(f"- **Pipeline stage:** {cite(d['stageId'])}")
    L.append(f"- **Priority:** {cite(d['priority'])}")
    L.append("")

    L.append("## Tasks")
    if not out["tasks"]:
        L.append("_none committed on the call_")
    for t in out["tasks"]:
        L.append(f"- **{t['title'].get('value', '(untitled)')}**")
        L.append(f"  - title: {cite(t['title'])}")
        L.append(f"  - due: {cite(t['dueAt'])}")
        L.append(f"  - notes: {cite(t['notes'])}")
    L.append("")

    L.append("## Notes")
    if not out["notes"]:
        L.append("_none_")
    for n in out["notes"]:
        L.append(f"- **[{n['category']}]** {cite(n['content'])}")
    L.append("")

    L.append("## Not mapped to any field")
    if not out["unmapped"]:
        L.append("_nothing left over — every business-relevant line mapped_")
    for u in out["unmapped"]:
        lns = ",".join(str(x) for x in u["source_lines"])
        L.append(f'- line {lns}: "{u["text"]}" — {u["reason"]}')
    L.append("")

    print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
