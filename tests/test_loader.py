import pytest
from pathlib import Path


def test_import():
    import pyphysbook_content
    assert pyphysbook_content.__version__ == "0.1.0"


def test_get_chapters():
    import pyphysbook_content
    chapters = pyphysbook_content.get_chapters()
    assert isinstance(chapters, list)
    assert len(chapters) == 7

    chapter_ids = [c["id"] for c in chapters]
    assert "ch01_python_basics" in chapter_ids
    assert "ch07_waves" in chapter_ids

    for ch in chapters:
        assert "id" in ch
        assert "title" in ch
        assert "sections" in ch
        assert isinstance(ch["sections"], list)


def test_get_section_code():
    import pyphysbook_content
    code = pyphysbook_content.get_section_code("ch01_python_basics", "01_hello.py")
    assert isinstance(code, str)
    assert "Hello" in code or "hello" in code.lower() or "print" in code


def test_get_section_path():
    import pyphysbook_content
    path = pyphysbook_content.get_section_path("ch01_python_basics", "01_hello.py")
    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "01_hello.py"


def test_chapter_titles():
    import pyphysbook_content
    chapters = pyphysbook_content.get_chapters()
    titles = [c["title"] for c in chapters]
    assert any("Python" in t for t in titles)
    assert any("力学" in t for t in titles)
    assert any("量子" in t for t in titles)


def test_sections_have_files():
    import pyphysbook_content
    chapters = pyphysbook_content.get_chapters()
    for ch in chapters:
        for sec in ch["sections"]:
            assert "file" in sec
            assert "title" in sec
            assert sec["file"].endswith(".py")


def test_all_section_files_exist():
    import pyphysbook_content
    chapters = pyphysbook_content.get_chapters()
    for ch in chapters:
        for sec in ch["sections"]:
            path = pyphysbook_content.get_section_path(ch["id"], sec["file"])
            assert path.exists(), f"Missing: {path}"


def test_nonexistent_chapter():
    import pyphysbook_content
    with pytest.raises(FileNotFoundError):
        pyphysbook_content.get_section_code("ch99_nonexistent", "01_test.py")


def test_get_version():
    import pyphysbook_content
    assert pyphysbook_content.get_version() == "0.1.0"
