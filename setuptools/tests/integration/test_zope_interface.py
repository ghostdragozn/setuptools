import platform
import subprocess
import sys
from inspect import cleandoc

import jaraco.path
import pytest

pytestmark = pytest.mark.integration

VIRTUALENV = (sys.executable, "-m", "virtualenv")


def run(cmd, **kwargs):
    proc = subprocess.run(cmd, encoding="utf-8", capture_output=True, **kwargs)
    if proc.returncode != 0:
        pytest.fail(f"Command {cmd} failed with:\n{proc.stdout=!s}\n{proc.stderr=!s}")
    return proc.stdout


@pytest.mark.skipif(
    platform.system() != "Linux",
    reason="only demonstrated to fail on Linux in #4399",
)
def test_interop_pkg_resources_iter_entry_points(tmp_path, venv):
    """
    Importing pkg_resources.iter_entry_points on console_scripts
    seems to cause trouble with zope-interface, when deprecates installation method
    is used. See #4399.
    """
    project = {
        "pkg": {
            "foo.py": cleandoc(
                """
                from pkg_resources import iter_entry_points

                def bar():
                    print("Print me if you can")
                """
            ),
            "setup.py": cleandoc(
                """
                from setuptools import setup, find_packages

                setup(
                    install_requires=["zope-interface==6.4.post2"],
                    entry_points={
                        "console_scripts": [
                            "foo=foo:bar",
                        ],
                    },
                )
                """
            ),
        }
    }
    jaraco.path.build(project, prefix=tmp_path)
    cmd = [venv.exe("pip"), "install", "-e", ".", "--no-use-pep517"]
    run(cmd, cwd=tmp_path / "pkg")
    out = run([venv.exe("foo")])
    assert "Print me if you can" in out
