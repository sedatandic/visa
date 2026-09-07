"""Olasi tanimsiz degisken taramasi (heuristik).

Bir isim yalnizca kosullu bir blokta (try/if/for/while/with) atanip sonrasinda
kullaniliyorsa bildirir. Blok oncesinde baglanmis, tum except'leri return/raise ile
sonlanan try'lar ve her iki dala da atanan isimler yanlis pozitif sayilmaz.

Kullanim: python scripts/possibly_unbound.py backend
"""

import ast
import sys
from pathlib import Path

CONDITIONAL = (ast.Try, ast.If, ast.For, ast.While, ast.AsyncFor)


def _stored(nodes: list) -> set[str]:
    names: set[str] = set()
    for node in nodes:
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                names.add(child.id)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                names.update((a.asname or a.name.split(".")[0]) for a in child.names)
            elif isinstance(child, ast.arg):
                names.add(child.arg)
    return names


def _terminates(body: list) -> bool:
    """Blok akisi kesin bitiyor mu (return/raise/continue/break)?"""
    return bool(body) and isinstance(body[-1], (ast.Return, ast.Raise, ast.Continue, ast.Break))


def _conditional_names(stmt: ast.stmt) -> set[str]:
    """Blok sonrasinda tanimsiz kalabilecek isimler."""
    if isinstance(stmt, ast.Try):
        if all(_terminates(h.body) for h in stmt.handlers) and stmt.handlers:
            return set()  # hata olursa akis bitiyor: try govdesi guvenli
        risky = _stored(stmt.body)
        for handler in stmt.handlers:
            risky -= _stored(handler.body)
        return risky - _stored(stmt.orelse + stmt.finalbody)
    if isinstance(stmt, ast.If):
        if not stmt.orelse:
            return _stored(stmt.body) if not _terminates(stmt.body) else set()
        if _terminates(stmt.body) or _terminates(stmt.orelse):
            return set()
        return _stored(stmt.body) ^ _stored(stmt.orelse)
    return _stored(stmt.body)  # for/while: govde hic calismayabilir


def check_function(func: ast.AST, path: Path) -> list[str]:
    findings = []
    bound = _stored(list(getattr(func, "args", ast.arguments(args=[])).args or []))
    bound |= {a.arg for a in getattr(func.args, "kwonlyargs", [])} if hasattr(func, "args") else set()
    body = list(func.body)
    # `global`/`nonlocal` isimleri modul duzeyinde bagli sayilir
    for node in ast.walk(func):
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            bound |= set(node.names)
    for index, stmt in enumerate(body):
        if isinstance(stmt, CONDITIONAL):
            risky = _conditional_names(stmt) - bound
            for later in body[index + 1 :]:
                used = {
                    n.id
                    for n in ast.walk(later)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
                }
                # Sonraki ifadenin kendi icinde atadigi isimler risk sayilmaz
                used -= _stored([later])
                for name in sorted(risky & used):
                    findings.append(f"{path}:{later.lineno}: '{name}' tanimsiz kalabilir")
                risky -= used
        bound |= _stored([stmt])
    return findings


def main(root: str) -> int:
    findings: list[str] = []
    for path in sorted(Path(root).rglob("*.py")):
        if "__pycache__" in str(path):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                findings.extend(check_function(node, path))
    print("\n".join(findings) or "temiz")
    print(f"toplam: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "backend"))
