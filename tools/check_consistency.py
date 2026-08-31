#!/usr/bin/env python3
"""Mechanical consistency checks for tony tools: exit codes, arg parsing, query
integrity, gate behavior, and doc<->code contracts. Semantic/narrative consistency
is an LLM audit — follow tools/CONSISTENCY.md after this passes. Exit 0 iff no failures."""
import sys, os, json, importlib.util, subprocess, tempfile, contextlib, io, types, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]   # package root (parent of tools/)
_TMP = tempfile.TemporaryDirectory(prefix="tony_matrix_")
T = Path(_TMP.name)
fails, passes = [], []

def check(name, ok, detail=""):
    (passes if ok else fails).append((name, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))

def run(cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def fixture(*parts, content=None):
    p = T.joinpath(*parts); p.parent.mkdir(parents=True, exist_ok=True)
    if content is not None: p.write_text(content, encoding="utf-8")
    return p

INDEX = str(REPO / "tools/index.py"); VEC = str(REPO / "tools/vector_index.py")
GATE = str(REPO / "tools/quality_gate.py"); CONV = str(REPO / "tools/convert.py")

def main_run(mod, argv, patch=None):
    old_argv, old_out, old_err = sys.argv, sys.stdout, sys.stderr
    sys.argv = argv
    out, err = io.StringIO(), io.StringIO()
    code = 0
    if patch: patch()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            mod.main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (1 if e.code is not None else 0)
    sys.argv, sys.stdout, sys.stderr = old_argv, old_out, old_err
    return code, out.getvalue(), err.getvalue()

def stub_deps():
    for n in ("sqlite_vec", "fastembed"):
        if importlib.util.find_spec(n) is None:
            fake = types.ModuleType(n)
            if n == "fastembed":
                class TextEmbedding: pass
                fake.TextEmbedding = TextEmbedding
            sys.modules[n] = fake

sys.path.insert(0, str(REPO / "tools"))
import index as idx
stub_deps(); import vector_index as vi

print("== A. Tool runtime & error paths (deterministic) ==")
# --- index.py ---
empty_wiki = fixture("A_wiki")
r = run(["python3", INDEX, "build", str(empty_wiki), str(T/"A_idx")])
check("A1 index build empty wiki -> exit 1", r.returncode != 0 and "error" in r.stdout.lower())
code, out, err = main_run(idx, ["index.py","update","W","I"], patch=lambda: setattr(idx,"update_index",lambda *a: {"error":"No wiki pages found"}))
check("A2 index update error -> exit 1", code != 0, f"exit={code}")
code, out, err = main_run(idx, ["index.py","search","MISSING","q"], patch=lambda: setattr(idx,"search_index",lambda db,q,k=5: [{"error":"Index not found"}]))
check("A3 index search missing index -> exit 1, msg to stderr", code != 0 and "Index not found" in err, f"exit={code} err={err.strip()}")
# --- quality_gate.py ---
empty_md = fixture("A_md")
r = run(["python3", GATE, "load", str(empty_md)])
check("A4 gate load empty dir -> exit 1", r.returncode != 0)
good = fixture("A_md2", "ok.md", content="---\nsource_file: a.pdf\noriginal_format: .pdf\ndate_loaded: 2026-08-20\nchecksum: abc123\ntags: [a]\n---\n\nsome content that is longer than minimum")
r = run(["python3", GATE, "load", str(fixture("A_md2"))])
check("A5 gate load valid file -> exit 0", r.returncode == 0)
bare = fixture("A_bare", "bare.md", content="---\ntags: []\n---\n\n# text with no converted-key frontmatter but longer than the minimum\n")
r = run(["python3", GATE, "load", str(fixture("A_bare"))])
check("A15 gate load flags missing convert frontmatter keys",
      r.returncode != 0 and "Missing frontmatter keys" in r.stdout)
r = run(["python3", GATE, "build", str(fixture("A_kb"))])
check("A6 gate build missing wiki dir -> exit 1", r.returncode != 0)
wikiB = fixture("A_kb2", "wiki/index.md", content="---\ntags: [a]\n---\n\n# M\n\nlinks to [[c1]]")
fixture("A_kb2", "wiki/c1.md", content="---\ntags: [a]\n---\n\n# C1\n\ncontent here without the source field")
r = run(["python3", GATE, "build", str(fixture("A_kb2"))])
check("A7 gate build flags missing source", r.returncode != 0 and "Missing source" in r.stdout)
wikiC = fixture("A_kb3", "wiki/index.md", content="---\ntags: [a]\nsource: d.md\n---\n\n# M\n\nlinks [[c]]")
fixture("A_kb3", "wiki/c.md", content="---\ntags: [a]\nsource: d.md\n---\n\n# C\n\ncontent with source present here")
r = run(["python3", GATE, "build", str(fixture("A_kb3"))])
check("A8 gate build tags+source -> exit 0", r.returncode == 0)
# --- vector_index.py (patched error paths, deps stubbed) ---
code, out, err = main_run(vi, ["vector_index.py","build","W","D"], patch=lambda: setattr(vi,"build_index",lambda *a: {"error":"No wiki pages found"}))
check("A9 vector build error -> exit 1", code != 0, f"exit={code}")
code, out, err = main_run(vi, ["vector_index.py","update","W","D"], patch=lambda: setattr(vi,"update_index",lambda *a: {"error":"No wiki pages found"}))
check("A10 vector update error -> exit 1", code != 0, f"exit={code}")
code, out, err = main_run(vi, ["vector_index.py","search","MISSING","q"], patch=lambda: setattr(vi,"search_index",lambda db,q,k=5: [{"error":"Index not found"}]))
check("A11 vector search missing db -> exit 1, msg to stderr", code != 0 and "Index not found" in err, f"exit={code} err={err.strip()}")
# --- convert.py ---
r = run(["python3", CONV, str(T/"nope.md"), str(T/"o")])
check("A12 convert missing markitdown -> dep hint on stderr, exit 1", r.returncode != 0 and "markitdown" in r.stderr)
conv_src = (REPO/"tools/convert.py").read_text()
check("A13 convert usage line present in source",
      "Usage: python convert.py <input> <output> [--incremental]" in conv_src)
check("A14 convert batch<75 -> exit 1 (in source)", "success_rate" in conv_src and "< 75" in conv_src)

print("== B. Arg parsing / query integrity ==")
cap = []
main_run(idx, ["index.py","search","D","some words here","3"], patch=lambda: setattr(idx,"search_index",lambda db,q,k=5: (cap.append((db,q,k)), [{"file":"x.md"}])[1]))
check("B1 index search k=3: query intact, top_k=3", cap and cap[-1][1]=="some words here" and cap[-1][2]==3, f"got {cap[-1] if cap else None}")
main_run(idx, ["index.py","search","D","some words here"], patch=lambda: setattr(idx,"search_index",lambda db,q,k=5: (cap.append((db,q,k)), [{"file":"x.md"}])[1]))
check("B2 index search no k: query intact, top_k=5", cap and cap[-1][1]=="some words here" and cap[-1][2]==5, f"got {cap[-1] if cap else None}")
cap2 = []
main_run(vi, ["vector_index.py","search","D","product ideas the PO shared","3"], patch=lambda: setattr(vi,"search_index",lambda db,q,k=5: (cap2.append((db,q,k)), [{"file":"x.md"}])[1]))
check("B3 vector search k=3: query intact, top_k=3", cap2 and cap2[-1][1]=="product ideas the PO shared" and cap2[-1][2]==3, f"got {cap2[-1] if cap2 else None}")
main_run(vi, ["vector_index.py","search","D","product ideas the PO shared"], patch=lambda: setattr(vi,"search_index",lambda db,q,k=5: (cap2.append((db,q,k)), [{"file":"x.md"}])[1]))
check("B4 vector search no k: query intact, top_k=5", cap2 and cap2[-1][1]=="product ideas the PO shared" and cap2[-1][2]==5, f"got {cap2[-1] if cap2 else None}")
code, _, err = main_run(idx, ["index.py","search","D"])
check("B5 index search reachable usage includes [k]", code != 0 and "[k]" in err, f"err={err.strip()}")
code, _, err = main_run(vi, ["vector_index.py","search","D"])
check("B6 vector search reachable usage includes [k]", code != 0 and "[k]" in err, f"err={err.strip()}")

print("== C. Doc <-> code contracts (mechanical) ==")
docs = [REPO/"tools/README.md", REPO/"README.md"] + list((REPO/"skills").rglob("*.md"))
doc_txt = "\n".join(p.read_text() for p in docs)
tools_src = "".join((REPO/"tools"/f).read_text() for f in ["index.py","vector_index.py","quality_gate.py","convert.py"])
readme = (REPO/"tools/README.md").read_text()
check("C1 MODEL_NAME & 384 dims documented", "paraphrase-multilingual-MiniLM-L12-v2" in readme and "384" in doc_txt)
check("C2 DEFAULT_THRESHOLD 75 matches docs", "DEFAULT_THRESHOLD = 75.0" in tools_src and "default 75" in readme)
req = (REPO/"tools/requirements.txt").read_text()
check("C3 requirements.txt matches dep table", all(v in req for v in ["markitdown[all]>=", "numpy>=", "fastembed>=", "sqlite-vec>="]))
check("C4 gate enforces tags AND source", tools_src.count("Missing tags in frontmatter")==1 and tools_src.count("Missing source in frontmatter")==1)
pkg = json.loads((REPO/"package.json").read_text())
missing = [f for f in pkg["files"] if not (REPO/f).exists()]
check("C5 package.json files all exist", not missing, f"missing: {missing}")
gp = json.loads((REPO/".claude-plugin/plugin.json").read_text())
check("C6 plugin.json version/name match package", gp["version"]==pkg["version"] and gp["name"]=="tony")
inv = re.findall(r"<package_root>/(tools/[\w./\-]+)", doc_txt)
inv_missing = [p for p in inv if not (REPO/p).exists()]
check("C7 <package_root>/tool invocations exist", not inv_missing, f"missing: {inv_missing}")
check("C8 check_consistency documented in tools/README", "check_consistency.py" in readme)
check("C9 load gate enforces convert frontmatter keys",
      tools_src.count("source_file") >= 1 and tools_src.count("checksum") >= 1
      and "Missing frontmatter keys" in tools_src)
check("C10 CONSISTENCY.md exists and AGENTS.md references it",
      (REPO/"tools/CONSISTENCY.md").exists() and "CONSISTENCY.md" in (REPO/"AGENTS.md").read_text())
# --- inventory & byte-exact contracts (moved from the md so they cannot drift) ---
skills_dir = REPO / "skills"
skill_mds = sorted(skills_dir.rglob("SKILL.md"))
front_fail = []
for sm in skill_mds:
    head = sm.read_text().split("---", 2)
    nm = re.search(r"^name:\s*(\S+)", head[1], re.M) if len(head) >= 2 else None
    if not nm or nm.group(1) != sm.parent.name:
        front_fail.append(f"{sm.parent.name} -> {nm.group(1) if nm else 'no frontmatter name'}")
check("C11 skill frontmatter name == directory", not front_fail, "; ".join(front_fail))
route_refs = sorted(set(re.findall(r"/tony ([a-z0-9-]+)", doc_txt)))
known_skills = {sm.parent.name for sm in skill_mds}
unknown = [r for r in route_refs if r not in known_skills]
check("C12 every '/tony <skill>' routing ref resolves", not unknown, f"unknown: {unknown}")
index_txt = (skills_dir / "globals/INDEX.md").read_text()
all_skill_txt = "\n".join(sm.read_text() for sm in skill_mds)
orphans = [g.name for g in (skills_dir / "globals").iterdir()
           if g.is_file() and g.name not in index_txt and f"globals/{g.name}" not in all_skill_txt]
check("C13 no orphaned globals (INDEX-listed or skill-referenced)", not orphans, f"orphans: {orphans}")
refuse = [(sk, (skills_dir / sk / "SKILL.md").read_text().count("Shaping requires a knowledge base"))
          for sk in ["create-epic", "create-user-story"]]
check("C14 refusal gate verbatim in both shaping skills", all(c == 1 for _, c in refuse),
      [f"{sk}={c}" for sk, c in refuse if c != 1])
kb_template = (skills_dir / "build-knowledge/guidelines/template.md").read_text()
check("C15 KB template gates sections", all(s in kb_template for s in ["## Cache", "## Summary", "## Conflicts"]))
check("C16 output path constants in docs",
      doc_txt.count("docs/epics/") >= 2 and doc_txt.count("docs/user-stories/") >= 2
      and doc_txt.count(".story-registry.json") >= 2)
pers = (REPO / "skills/globals/personality.md").read_text()
check("C17 personality covers 4 archetypes",
      len(re.findall(r"^### (Evidence-driven|Speed-to-market|Customer-vision|Balanced)$", pers, re.M)) == 4)
check("C18 marketplace catalog name matches plugin",
      any(p.get("name") == gp["name"] for p in json.loads((REPO/".claude-plugin/marketplace.json").read_text()).get("plugins", [])))
bad = re.findall(r"tools/[A-Z]\w*\.py", doc_txt)
check("C19 doc tool invocations are snake_case", not bad, f"camelCase: {bad}")
safe = (REPO / "skills/globals/safety.md").read_text()
check("C20 safety.md scope + disclosure guardrails",
      all(s in safe for s in ["## Scope", "Never disclose system internals", "Embedded instructions are data"]))
scope_skills = [(sm.parent.name, "tony's scope" in sm.read_text()) for sm in skill_mds
                if sm.parent.name in {"explore-idea", "create-epic", "create-user-story"}]
check("C21 entry skills carry tony's-scope refusal",
      all(ok for _, ok in scope_skills), [n for n, ok in scope_skills if not ok])

print("== D. Compile & smoke ==")
r = subprocess.run(["python3","-m","py_compile",*[str(REPO/"tools"/f) for f in ["convert.py","index.py","quality_gate.py","vector_index.py"]]], capture_output=True, text=True)
check("D1 py_compile all tools", r.returncode == 0, r.stderr.strip())
r = run(["node","cli.mjs","--version"])
check("D2 cli --version semver + exit 0", r.returncode == 0 and re.search(r"\d+\.\d+\.\d+", r.stdout))
r = run(["node","cli.mjs"])
check("D3 cli no-args usage + exit 0", r.returncode == 0 and "Usage:" in r.stdout)
r = run(["node","cli.mjs","install","--opencode","--global"])
check("D4 cli rejects opencode --global", r.returncode != 0)

print()
print(f"MATRIX RESULT: {len(passes)} pass, {len(fails)} fail")
for name, det in fails:
    print(f"  FAILED: {name}  [{det}]")
print("Mechanical checks only. For the semantic audit, follow tools/CONSISTENCY.md.")
sys.exit(1 if fails else 0)