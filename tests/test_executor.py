import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "pyphysbook-ide", "src"))


def test_executor_import():
    from pyphysbook_ide.runner.executor import Executor
    assert Executor is not None


def test_executor_creation():
    from pyphysbook_ide.runner.executor import Executor
    executor = Executor()
    assert not executor.is_running()


def test_executor_signals():
    from pyphysbook_ide.runner.executor import Executor
    executor = Executor()
    assert hasattr(executor, "execution_started")
    assert hasattr(executor, "execution_finished")
    assert hasattr(executor, "stdout_ready")
    assert hasattr(executor, "stderr_ready")


def test_ide_import():
    from pyphysbook_ide import __version__
    assert __version__ == "0.1.0"


def test_app_import():
    from pyphysbook_ide.app import main
    assert callable(main)
