"""编辑区可插拔架构：EditorView 接口 + EditorProvider + EditorRegistry。

仿 VS Code Custom Editors：编辑区是宿主，具体内容由注册的 provider 提供。
新增一种文件类型的查看器，只需实现 EditorView 并注册一个 EditorProvider，
无需改动 MainWindow / TabManager。
"""
import os


class EditorView:
    """所有标签页内容（编辑器/查看器）实现的统一接口。

    作为 mixin 与 QWidget 派生类混入（不自带 __init__，避免干扰 Qt 构造）。
    子类按需覆写方法；未覆写者使用此处的只读/空操作默认实现。
    """

    # 当前文件路径（子类通常实现为 property）
    file_path = None

    # 非文件型标签页（设置页、欢迎页等插件面板）的唯一标识；
    # 文件型视图为 None。
    panel_id = None

    def editor_title(self) -> str:
        """标签基础标题（不含前缀/星号）。"""
        if self.file_path:
            return os.path.basename(self.file_path)
        return "未命名"

    def is_modified(self) -> bool:
        """是否有未保存修改（只读查看器返回 False）。"""
        return False

    def is_readonly(self) -> bool:
        """是否只读（影响保存按钮可用性）。默认查看器只读。"""
        return True

    def save(self) -> bool:
        """保存到磁盘。返回是否已保存（只读查看器返回 False）。"""
        return False

    def cleanup(self):
        """关闭标签时释放资源（如关闭文件句柄）。"""
        pass

    def apply_theme(self, theme_name: str):
        """主题切换通知。"""
        pass

    def apply_editor_prefs(self):
        """字号/缩进等编辑器偏好变更通知。"""
        pass


class EditorProvider:
    """为某类文件提供 EditorView 的提供者。"""
    id = ""
    extensions = ()          # 小写扩展名（含点），如 (".pdf",)
    priority = 0             # 多个命中时，priority 大者优先
    title_prefix = ""        # 标签标题前缀（如 "📄"）
    readonly = True          # 该类型默认是否只读

    def can_open(self, path: str) -> bool:
        if self.extensions:
            return os.path.splitext(path)[1].lower() in self.extensions
        return False

    def create(self, path: str, parent=None) -> EditorView:
        raise NotImplementedError


class EditorRegistry:
    """EditorProvider 注册表与分发器。"""

    _FALLBACK_PRIORITY = -1000

    def __init__(self):
        self._providers = []

    def register(self, provider: EditorProvider):
        if provider not in self._providers:
            self._providers.append(provider)
        # priority 高的在前；同优先级保持注册顺序
        self._providers.sort(key=lambda p: -p.priority)

    def unregister(self, provider_id: str):
        self._providers = [p for p in self._providers if p.id != provider_id]

    def select(self, path: str):
        for provider in self._providers:      # 已按 priority 降序
            if provider.can_open(path):
                return provider
        return None

    def open(self, path: str, parent=None):
        provider = self.select(path)
        if provider is None:
            return None
        return provider.create(path, parent)

    def title_for(self, path: str) -> str:
        provider = self.select(path)
        name = os.path.basename(path)
        if provider and provider.title_prefix:
            return f"{provider.title_prefix} {name}"
        return name

    @property
    def providers(self):
        return list(self._providers)


registry = EditorRegistry()
