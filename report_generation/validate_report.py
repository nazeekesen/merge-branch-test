#!/usr/bin/env python3
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
    """
    Returns:
      outline: List[Tuple[level:int, title_slug:str]]
      blocks_by_section: Dict[index_in_outline, List[str]]  (coarse block types)
    """
    lines = text.splitlines()
    outline: List[Tuple[int, str]] = []
    # For block typing we segment by headings
    sections: List[Tuple[int, int]] = []  # (start_line, end_line) per heading content (exclusive)
    heading_lines: List[int] = []

    # find headings
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m:
            lvl = len(m.group(1))
            title = slugify(m.group(2))
            outline.append((lvl, title))
            heading_lines.append(i)

    # if no headings, it's invalid structure for our template use-case
    if not outline:
        return outline, {}

    # build section line ranges (content after each heading until next heading or EOF)
    heading_lines.append(len(lines))
    for idx in range(len(heading_lines) - 1):
        start = heading_lines[idx] + 1
        end = heading_lines[idx + 1]
        sections.append((start, end))

    # classify coarse block types per section
    blocks_by_section: Dict[int, List[str]] = {}
    for si, (start, end) in enumerate(sections):
        block_seq: List[str] = []
        in_code = False
        i = start
        while i < end:
            ln = lines[i]
            # code fences
            if CODE_FENCE.match(ln):
                in_code = not in_code
                if not block_seq or block_seq[-1] != 'code':
                    block_seq.append('code')
                i += 1
                continue
            if in_code:
                i += 1
                continue

            # tables (detect by separator line or typical table row with pipes)
            if '|' in ln:
                # Peek next line to see a header separator
                nxt = lines[i+1] if i + 1 < end else ''
                if TABLE_SEP.match(nxt) or '|' in nxt:
                    if not block_seq or block_seq[-1] != 'table':
                        block_seq.append('table')
                    # consume contiguous table-ish lines
                    while i < end and '|' in lines[i]:
                        i += 1
                    continue

            # lists
            if LIST_RE.match(ln):
                if not block_seq or block_seq[-1] != 'list':
                    block_seq.append('list')
                # consume contiguous list lines
                while i < end and (LIST_RE.match(lines[i]) or not lines[i].strip()):
                    i += 1
                continue

            # images
            if ln.strip().startswith('!['):
                if not block_seq or block_seq[-1] != 'image':
                    block_seq.append('image')
                i += 1
                continue

            # paragraphs (non-empty text)
            if ln.strip():
                if not block_seq or block_seq[-1] != 'para':
                    block_seq.append('para')
            i += 1

        # compress very long para sequences to a single 'para'
        blocks_by_section[si] = block_seq

    return outline, blocks_by_section

def compare_outlines(ref: List[Tuple[int,str]], got: List[Tuple[int,str]]) -> List[str]:
    errs: List[str] = []
    if len(ref) != len(got):
        errs.append(f'Heading count mismatch: expected {len(ref)}, got {len(got)}')
    # Compare pairwise but also report extras/missing
    L = min(len(ref), len(got))
    for i in range(L):
        rl, rt = ref[i]
        gl, gt = got[i]
        if rl != gl or rt != gt:
            errs.append(f'Heading #{i+1} differs:\n'
                        f'  expected: H{rl} "{rt}"\n'
                        f'  got     : H{gl} "{gt}"')
    # trailing diffs
    if len(got) > len(ref):
        extras = [f'H{l} "{t}"' for (l,t) in got[len(ref):]]
        errs.append('Extra headings found: ' + ', '.join(extras))
    if len(ref) > len(got):
        missing = [f'H{l} "{t}"' for (l,t) in ref[len(got):]]
        errs.append('Missing headings: ' + ', '.join(missing))
    return errs

def soft_compare_blocks(ref_blocks: Dict[int,List[str]], got_blocks: Dict[int,List[str]], ref_outline) -> List[str]:
    """
    Loose check: ensure each section’s block-type *order* is compatible.
    We allow additional paragraphs but keep the relative sequence (e.g., para → table → list).
    """
    errs: List[str] = []
    for i in range(min(len(ref_blocks), len(got_blocks))):
        ref_seq = ref_blocks[i]
        got_seq = got_blocks[i]
        # allow collapsing consecutive 'para' and ignoring extra paras
        def normalize(seq):
            out = []
            for x in seq:
                if x == 'para':
                    if not out or out[-1] != 'para':
                        out.append('para')
                else:
                    out.append(x)
            return out
        r = normalize(ref_seq)
        g = normalize(got_seq)

        # Check that r is a subsequence of g preserving order
        it = iter(g)
        ok = True
        for x in r:
            for y in it:
                if y == x:
                    break
            else:
                ok = False
                break
        if not ok:
            hlevel, htitle = ref_outline[i]
            errs.append(
                f'Section "{htitle}" structure differs. '
                f'Expected order like: {r}, got: {g}'
            )
    return errs

def main():
    if len(sys.argv) != 3:
        print("Usage: validate_report.py <original.md> <candidate.md>")
        sys.exit(2)

    ref_path, got_path = sys.argv[1], sys.argv[2]
    ref = open(ref_path, 'r', encoding='utf-8').read()
    got = open(got_path, 'r', encoding='utf-8').read()

    ref_outline, ref_blocks = parse_outline_and_blocks(ref)
    got_outline, got_blocks = parse_outline_and_blocks(got)

    errs = []
    # 1) strict heading/ordering check
    errs += compare_outlines(ref_outline, got_outline)

    # 2) loose block-shape check (optional but helpful)
    errs += soft_compare_blocks(ref_blocks, got_blocks, ref_outline)

    if errs:
        print("STRUCTURE CHECK FAILED\n")
        for e in errs:
            print("-", e)
        print("\nTip: headings must match exactly (text & level). Wording inside sections can differ.")
        sys.exit(1)

    print("Structure check passed: headings and basic layout match.")
    sys.exit(0)

if __name__ == "__main__":
    main()
