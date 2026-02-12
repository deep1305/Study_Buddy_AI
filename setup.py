from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup


def read_requirements(path: str = "requirements.in") -> list[str]:
    """
    Read top-level requirements (one per line).

    Use `requirements.in` here (NOT the compiled `requirements.txt`), because the
    compiled file contains indented '# via ...' lines that are not valid for
    install_requires.
    """
    p = Path(__file__).parent / path
    if not p.exists():
        return []

    reqs: list[str] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        reqs.append(line)
    return reqs


setup(
    name="study-buddy-ai",
    version="0.1.0",
    description="A study buddy AI",
    author="Deep",
    python_requires=">=3.12",
    packages=find_packages(),
    install_requires=read_requirements("requirements.in"),
)