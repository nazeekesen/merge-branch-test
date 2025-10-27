#!/usr/bin/env python3
"""
fix_report.py

Take a template (reference) Markdown and a candidate Markdown.
Produce a "fixed" candidate whose headings (text & level) and section order
match the template. Section bodies are preserved from the candidate where
we can map them by heading slug; missing sections are created with a stub
(unless --no-placeholder). Extra sections can be appended at the end or
dropped with --drop-extra.

Usage:
  python3 fix_report.py template.md candidate.md -o fixed.md
  python3 fix_report.py template.md candidate.md --inplace
  python3 fix_report.py template.md candidate.md --inplace --no-placeholder --drop-extra
"""

import sys, re, os
from typing import List, Tuple, Dict

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
LIST_RE    = re.compile(r'^\s*(?:[-*+]|\d+\.)\s+')
TABLE_SEP  = re.compile(r'^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$')
CODE_FENCE = re.compile(r'^\s*```')

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'`.+?`', '', s)              # remove inline code
    s = re.sub(r'[^a-z0-9\s-]', '', s)       # keep alnum/space/hyphen
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_outline_and_blocks(text: str):
    lines = text.splitlines()
    outline: List[Tuple[int, str]] = []
    sections: List[Tuple[int, int]] = []
    heading_lines: List[int] = []

    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m:
            lvl = len(m.group(1))
            title = slugify(m.group(2))
            outline.append((lvl, title))
            heading_lines.append(i)

    if not outline:
        return outline, {}, lines, heading_lines

    heading_lines.append(len(lines))
    for idx in range(len(heading_lines) - 1):
        start = heading_lines[idx] + 1
        end = heading_lines[idx + 1]
        sections.append((start, end))

    blocks_by_section: Dict[int, List[str]] = {}
    for si, (start, end) in enumerate(sections):
        block_seq: List[str] = []
        in_code = False
        i = start
        while i < end:
            ln = lines[i]
            if CODE_FENCE.match(ln):
                in_code = not in_code
                if not block_seq or block_seq[-1] != 'code':
                    block_seq.append('code')
                i += 1
                continue
            if in_code:
                i += 1
                continue

            if '|' in ln:
                nxt = lines[i+1] if i + 1 < end else ''
                if TABLE_SEP.match(nxt) or '|' in nxt:
                    if not block_seq or block_seq[-1] != 'table':
                        block_seq.append('table')
                    while i < end and '|' in lines[i]:
                        i += 1
                    continue

            if LIST_RE.match(ln):
                if not block_seq or block_seq[-1] != 'list':
                    block_seq.append('list')
                while i < end and (LIST_RE.match(lines[i]) or not lines[i].strip()):
                    i += 1
                continue

            if ln.strip().startswith('!['):
                if not block_seq or block_seq[-1] != 'image':
                    block_seq.append('image')
                i += 1
                continue

            if ln.strip():
                if not block_seq or block_seq[-1] != 'para':
                    block_seq.append('para')
            i += 1

        blocks_by_section[si] = block_seq

    return outline, blocks_by_section, lines, heading_lines[:-1]

def extract_sections(text: str):
    lines = text.splitlines()
    headings: List[Tuple[int, str, str, int]] = []
    heading_idxs: List[int] = []
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m:
            level = len(m.group(1))
            title_text = m.group(2).strip()
            headings.append((level, title_text, slugify(title_text), i))
            heading_idxs.append(i)

    preamble: List[str] = []
    if heading_idxs:
        if heading_idxs[0] > 0:
            preamble = lines[:heading_idxs[0]]
    else:
        preamble = lines

    body_by_slug: Dict[str, List[str]] = {}
    if heading_idxs:
        indices = heading_idxs + [len(lines)]
        for h_idx, start_line in enumerate(heading_idxs):
            _, title_text, title_slug, _ = headings[h_idx]
            start = start_line + 1
            end = indices[h_idx + 1]
            body_by_slug[title_slug] = lines[start:end]

    return headings, body_by_slug, preamble

def rebuild_to_template(
    template_text: str,
    candidate_text: str,
    insert_placeholder: bool = True,
    placeholder_text: str = "_This section was missing in the source and was created to match the template._",
    drop_extra: bool = False,
):
    # Parse template headings (levels + original text)
    _, _, t_lines, _ = parse_outline_and_blocks(template_text)
    template_heads: List[Tuple[int, str]] = []
    for ln in t_lines:
        m = HEADING_RE.match(ln)
        if m:
            lvl = len(m.group(1))
            title = m.group(2).strip()
            template_heads.append((lvl, title))

    # Candidate sections
    c_heads, c_bodies, c_preamble = extract_sections(candidate_text)

    # Map candidate by slug -> (level, title_text)
    cand_by_slug: Dict[str, Tuple[int, str]] = {}
    for lvl, ttext, tslug, _ in c_heads:
        cand_by_slug[tslug] = (lvl, ttext)

    used_slugs = set()
    report: Dict[str, List[str]] = {
        "added": [], "renamed": [], "reordered": [], "extra_appended": [], "preamble_kept": []
    }

    out_lines: List[str] = []

    # Keep preamble if present (optional)
    if any(s.strip() for s in c_preamble):
        out_lines.extend(c_preamble)
        if out_lines and out_lines[-1].strip() != "":
            out_lines.append("")
        report["preamble_kept"].append(f"{len(c_preamble)} preamble lines kept")

    # Emit sections in template order
    for lvl, title_text in template_heads:
        slug = slugify(title_text)
        used_slugs.add(slug)
        out_lines.append("#" * lvl + " " + title_text)

        if slug in c_bodies:
            body = c_bodies[slug]
            if slug in cand_by_slug:
                orig_level, orig_title = cand_by_slug[slug]
                if orig_level != lvl or orig_title.strip() != title_text.strip():
                    report["renamed"].append(f'"{orig_title}" (H{orig_level}) -> "{title_text}" (H{lvl})')
            out_lines.extend(body)
        else:
            if insert_placeholder:
                out_lines.append("")
                out_lines.append(placeholder_text)
                out_lines.append("")
                report["added"].append(f'Added missing section "{title_text}" (H{lvl})')
            # else: leave empty

        if out_lines and out_lines[-1].strip() != "":
            out_lines.append("")

    # Handle extra (unmatched) sections
    extra_slugs = [s for s in c_bodies.keys() if s not in used_slugs]
    if extra_slugs and not drop_extra:
        out_lines.append("# Unmatched sections from source")
        for s in extra_slugs:
            body = c_bodies[s]
            lvl, orig_title = cand_by_slug.get(s, (2, s))
            out_lines.append("## " + orig_title)
            out_lines.extend(body)
            if out_lines and out_lines[-1].strip() != "":
                out_lines.append("")
            report["extra_appended"].append(orig_title)

    # If we kept counts equal but order was different, note it
    if len(c_heads) == len(template_heads):
        template_slugs = [slugify(t) for _, t in template_heads]
        cand_slugs = [slugify(t) for _, t, _, _ in c_heads]
        if template_slugs != cand_slugs:
            report["reordered"].append("Sections were reordered to match the template")

    fixed_text = "\n".join(out_lines).rstrip() + "\n"
    return fixed_text, report

def main():
    import argparse
    p = argparse.ArgumentParser(description="Fix a Markdown report to match a template's structure.")
    p.add_argument("template", help="Template/reference Markdown")
    p.add_argument("candidate", help="Candidate Markdown to fix")
    p.add_argument("-o", "--output", help="Output path for fixed file (default: candidate_fixed.md)")
    p.add_argument("--inplace", action="store_true", help="Overwrite candidate in place")
    p.add_argument("--no-placeholder", action="store_true", help="Do not insert placeholder text for missing sections")
    p.add_argument("--drop-extra", action="store_true", help="Drop extra unmatched sections instead of appending them")
    args = p.parse_args()

    with open(args.template, "r", encoding="utf-8") as f:
        template_text = f.read()
    with open(args.candidate, "r", encoding="utf-8") as f:
        candidate_text = f.read()

    fixed, report = rebuild_to_template(
        template_text,
        candidate_text,
        insert_placeholder=not args.no_placeholder,
        drop_extra=args.drop_extra,
    )

    out_path = args.candidate if args.inplace else (args.output or os.path.splitext(args.candidate)[0] + "_fixed.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(fixed)

    def print_list(label: str, items: List[str]):
        if items:
            print(f"{label}:")
            for it in items:
                print(f"  - {it}")

    print(f"Written fixed file: {out_path}")
    print_list("Added sections", report.get("added", []))
    print_list("Renamed to match template", report.get("renamed", []))
    print_list("Reordered", report.get("reordered", []))
    print_list("Extra sections appended", report.get("extra_appended", []))
    print_list("Notes", report.get("preamble_kept", []))

if __name__ == "__main__":
    main()
