import pytest
from pathlib import Path


def test_import():
    import npworks_content
    assert npworks_content.__version__ == "0.0.2"


def test_get_chapters():
    import npworks_content
    chapters = npworks_content.get_chapters()
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
    import npworks_content
    code = npworks_content.get_section_code("ch01_python_basics", "01_hello.py")
    assert isinstance(code, str)
    assert "Hello" in code or "hello" in code.lower() or "print" in code


def test_get_section_path():
    import npworks_content
    path = npworks_content.get_section_path("ch01_python_basics", "01_hello.py")
    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "01_hello.py"


def test_chapter_titles():
    import npworks_content
    chapters = npworks_content.get_chapters()
    titles = [c["title"] for c in chapters]
    assert any("Python" in t for t in titles)
    assert any("力学" in t for t in titles)
    assert any("量子" in t for t in titles)


def test_sections_have_files():
    import npworks_content
    chapters = npworks_content.get_chapters()
    for ch in chapters:
        for sec in ch["sections"]:
            assert "file" in sec
            assert "title" in sec
            assert sec["file"].endswith(".py")


def test_all_section_files_exist():
    import npworks_content
    chapters = npworks_content.get_chapters()
    for ch in chapters:
        for sec in ch["sections"]:
            path = npworks_content.get_section_path(ch["id"], sec["file"])
            assert path.exists(), f"Missing: {path}"


def test_nonexistent_chapter():
    import npworks_content
    with pytest.raises(FileNotFoundError):
        npworks_content.get_section_code("ch99_nonexistent", "01_test.py")


def test_get_version():
    import npworks_content
    assert npworks_content.get_version() == "0.0.2"
