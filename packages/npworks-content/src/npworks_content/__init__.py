"""npworks-content: NPworks — 计算物理交互式教材内容"""

__version__ = "0.0.2"

from npworks_content.loader import ContentLoader

_loader = ContentLoader()

def get_chapters():
    return _loader.get_chapters()

def get_section_code(chapter_id: str, filename: str) -> str:
    return _loader.get_section_code(chapter_id, filename)

def get_section_path(chapter_id: str, filename: str):
    return _loader.get_section_path(chapter_id, filename)

def get_version() -> str:
    return __version__
