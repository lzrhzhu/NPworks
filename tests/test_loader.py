import pytest
from pathlib import Path


def test_import():
    import npworks_content
    assert npworks_content.__version__ == "0.0.2"


def _chapters():
    import npworks_content
    return npworks_content.get_chapters()


def test_get_chapters_nonempty():
    chapters = _chapters()
    assert isinstance(chapters, list)
    assert len(chapters) >= 20  # 教材章节数随版本增长

    ids = [c["id"] for c in chapters]
    assert "ch02_air_motion" in ids
    assert "ch09_ising" in ids
    assert "ch16_stationary_schrodinger" in ids

    for ch in chapters:
        assert "id" in ch
        assert "title" in ch
        assert "description" in ch
        assert "sections" in ch
        assert isinstance(ch["sections"], list)
        assert ch["sections"], f"章节 {ch['id']} 没有任何小节"


def test_chapter_titles():
    titles = [c["title"] for c in _chapters()]
    assert any("物理" in t for t in titles)
    assert any("力学" in t for t in titles)
    assert any(("量子" in t) or ("薛定谔" in t) for t in titles)


def test_sections_have_files():
    for ch in _chapters():
        for sec in ch["sections"]:
            assert "file" in sec
            assert "title" in sec
            assert sec["file"].endswith(".py")


def test_all_section_files_exist():
    import npworks_content
    for ch in _chapters():
        for sec in ch["sections"]:
            path = npworks_content.get_section_path(ch["id"], sec["file"])
            assert path.exists(), f"Missing: {path}"


def test_get_section_code():
    import npworks_content
    code = npworks_content.get_section_code("ch02_air_motion", "01_bicycle_no_drag.py")
    assert isinstance(code, str)
    assert "import" in code or "matplotlib" in code


def test_get_section_path():
    import npworks_content
    path = npworks_content.get_section_path("ch02_air_motion", "01_bicycle_no_drag.py")
    assert isinstance(path, Path)
    assert path.exists()
    assert path.name == "01_bicycle_no_drag.py"


def test_nonexistent_chapter():
    import npworks_content
    with pytest.raises(FileNotFoundError):
        npworks_content.get_section_code("ch99_nonexistent", "01_test.py")


def test_get_version():
    import npworks_content
    assert npworks_content.get_version() == "0.0.2"
