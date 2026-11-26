"""Gather strategy files from cloned sources: one file per strategy class, duplicates removed.
Usage: python collect.py <sources_dir> <out_dir>  -> writes out_dir/*.py and out_dir/manifest.json"""
import ast, hashlib, json, os, re, sys

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
SKIP_DIRS = ("hyperopt", "test", "/.git")


def strategy_classes(tree):
    out = []
    for n in tree.body:
        if isinstance(n, ast.ClassDef):
            bases = [getattr(b, "id", getattr(b, "attr", "")) for b in n.bases]
            out.append((n.name, bases))
    return out


def fingerprint(code):
    """Same logic, different comments/whitespace/class name -> same fingerprint."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef):
            n.name = "X"
        if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Module)) and n.body and isinstance(n.body[0], ast.Expr) \
                and isinstance(getattr(n.body[0], "value", None), ast.Constant) and isinstance(n.body[0].value.value, str):
            n.body = n.body[1:] or [ast.Pass()]
    return hashlib.sha1(ast.dump(tree).encode()).hexdigest()


seen_fp, seen_name, manifest, stats = {}, set(), [], {"files": 0, "no_class": 0, "dup_logic": 0, "dup_name": 0, "syntax": 0, "multi": 0}
for root, _, files in os.walk(src):
    if any(s in root.lower() for s in SKIP_DIRS):
        continue
    for f in sorted(files):
        if not f.endswith(".py"):
            continue
        path = os.path.join(root, f)
        try:
            code = open(path, encoding="utf-8", errors="replace").read()
            tree = ast.parse(code)
        except SyntaxError:
            stats["syntax"] += 1
            continue
        stats["files"] += 1
        cls = [c for c, b in strategy_classes(tree) if "IStrategy" in b]
        if not cls:
            stats["no_class"] += 1
            continue
        if len(cls) > 1:
            stats["multi"] += 1           # keep the first; subclasses of it are variants we skip
        name = cls[0]
        fp = fingerprint(code)
        if fp in seen_fp:
            stats["dup_logic"] += 1
            continue
        if name in seen_name:
            stats["dup_name"] += 1        # different code, same class name: keep under a suffixed file
            name2 = f"{name}__{hashlib.sha1(code.encode()).hexdigest()[:6]}"
            code = re.sub(rf"\bclass {name}\(", f"class {name2}(", code, count=1)
            name = name2
        seen_fp[fp] = name
        seen_name.add(name)
        open(os.path.join(out, name + ".py"), "w", encoding="utf-8").write(code)
        manifest.append({"strategy": name, "source": os.path.relpath(path, src)})
json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
print(stats, "kept", len(manifest))
