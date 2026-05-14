import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "npworks-ide", "src"))


def test_executor_import():
    from npworks_ide.runner.executor import Executor
    assert Executor is not None


def test_executor_creation():
    from npworks_ide.runner.executor import Executor
    executor = Executor()
    assert not executor.is_running()


def test_executor_signals():
    from npworks_ide.runner.executor import Executor
    executor = Executor()
    assert hasattr(executor, "execution_started")
    assert hasattr(executor, "execution_finished")
    assert hasattr(executor, "stdout_ready")
    assert hasattr(executor, "stderr_ready")


def test_ide_import():
    from npworks_ide import __version__
    assert __version__ == "0.0.3"


def test_app_import():
    from npworks_ide.app import main
    assert callable(main)
