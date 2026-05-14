from pathlib import Path

import yaml


class ContentLoader:
    def __init__(self):
        self._content_dir = Path(__file__).parent / "content"

    def get_chapters(self) -> list:
        chapters = []
        if not self._content_dir.exists():
            return chapters
        for item in sorted(self._content_dir.iterdir()):
            if item.is_dir() and item.name.startswith("ch"):
                meta_path = item / "meta.yaml"
                if meta_path.exists():
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = yaml.safe_load(f)
                    sections = meta.get("sections", [])
                    chapters.append({
                        "id": item.name,
                        "title": meta.get("title", item.name),
                        "description": meta.get("description", ""),
                        "sections": sections,
                    })
        return chapters

    def get_section_code(self, chapter_id: str, filename: str) -> str:
        path = self.get_section_path(chapter_id, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def get_section_path(self, chapter_id: str, filename: str) -> Path:
        return self._content_dir / chapter_id / filename
