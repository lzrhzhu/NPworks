# npworks-ide 重构计划（第 3、4 步）

> 版本: 1.0 | 范围: `npworks/packages/npworks-ide` | 前置: 第 1、2 步已完成（死代码清理 + EnvController 抽取）

本文件是**可执行的修改计划**，不是设计草案。每一步都给出：目标、精确的方法/文件清单、迁移顺序、调用点修改表、验证手段与回滚策略。两步**相互独立**，建议先做第 3 步（影响面小、收益直接）再做第 4 步（结构性、需分批）。

---

## 当前基线（重构前快照）

- `main_window.py`：**887 行**，仍混合 5 类职责（布局装配 / 栏位可见性 / 原生窗口 / 状态栏 / 文件标签回调）。
- `ide/` 包：**35 个模块**全部平铺在一层目录。
- 已具备控制器层：`run_controller` / `find_controller` / `edit_controller` / `theme_controller` / `actions` / `env_controller`。
- 已具备子包：`themes/`、`runner/`。
- 已确认的死文件 `bottom_panel.py` / `outline_view.py` / `sidebar_panel.py` / `theme.py` 因文件锁未物理删除，但**零引用**，不影响本计划（第 4 步执行前应先手动删除它们）。

---

# 第 3 步：抽出 LayoutManager

## 3.1 目标

把 `main_window.py` 中所有「停靠栏位 / 分割条 / 面板可见性 / 布局恢复」逻辑迁入 `ide/layout_manager.py` 的 `LayoutManager` 类，与既有控制器风格一致。

**预期效果**：`main_window.py` 从 887 行降至约 **600–650 行**；`LayoutManager` 约 **240 行**。

## 3.2 迁移方法清单（精确到方法名 + 当前行号）

下表所有方法当前位于 `ide/main_window.py`，按职责分组：

| 分组 | 方法 | 当前行 | 备注 |
|------|------|--------|------|
| 常量 | `_ZONE_LAYOUT` | 44–48 | 模块级常量，随类一起迁出 |
| 分割条/栏位 | `_zone_splitter_index` | 355 | |
| | `_is_zone_visible` | 359 | |
| | `_set_zone_visible` | 363 | 核心可见性切换 |
| | `_ensure_panel_zone_visible` | 375 | |
| 面板显示 | `_show_panel` | 381 | |
| | `_show_output_panel` | 390 | |
| | `_toggle_bottom_panel` | 798 | |
| 自动调整 | `_auto_adjust_zones` | 343 | |
| | `_on_panel_moved` | 339 | DockManager 信号槽 |
| | `_sync_zone_actions` | 622 | 同步视图菜单勾选 |
| 图标 | `_icon_for_key` | 332 | |
| | `_refresh_sidebar_icons` | 589 | |
| 激活（面板↔活动栏） | `_ACTIVITY_PANEL` | 538 | 类常量 |
| | `_activate_panel` | 546 | |
| | `_activate_view` | 567 | 兼容旧名，保留为转发 |
| | `_toggle_figures_dock` | 570 | |
| | `_on_figure_ready` | 581 | |
| 外观访问器 | `_persist` | 619 | |
| | `is_primary_sidebar` / `set_primary_sidebar` | 627 / 630 | |
| | `is_figures_dock` / `set_figures_dock` | 635 / 639 | |
| | `is_secondary_sidebar` / `set_secondary_sidebar` | 646 / 649 | |
| | `is_panel` / `set_panel` | 670 / 673 | |
| | `is_view_visible` / `set_view_visible` | 678 / 681 | |
| 恢复 | `_restore_appearance` | 701 | 仅栏位/可见性部分 |
| | `_restore_layout` | 1017 | 分割条尺寸 |

**留在 MainWindow**（不属于布局）：`is_menu_bar`/`set_menu_bar`、`is_status_bar`/`set_status_bar`（菜单栏/状态栏可见性，各 2 行，归属 MainWindow 本身）、`_restore_geometry`、`_setup_layout`（**仅控件创建与分割条装配**，面板注册逻辑改为调用 `layout.register_panels(...)`）、`_build_status_bar`、`_connect_signals`、`__init__`、文件/标签回调、命令面板、`closeEvent`。

## 3.3 LayoutManager 接口设计

```python
# ide/layout_manager.py（骨架）
class LayoutManager:
    def __init__(self, main_window):
        self._mw = main_window
        self.dock = main_window.dock                # DockManager
        self._h = main_window._h_splitter
        self._v = main_window._v_splitter
        self._zone_actions = main_window._zone_actions  # dict 复用同一引用
        self._activity_bar = main_window.activity_bar

    # 控件创建完成后由 MainWindow 调用，集中注册面板
    def register_panels(self, spec):
        """spec: [(panel_id, widget, title, zone, icon_key), ...]"""
        ...

    # --- 栏位可见性 ---
    def zone_splitter_index(self, name): ...
    def is_zone_visible(self, name): ...
    def set_zone_visible(self, name, on): ...

    # --- 面板显示/聚焦 ---
    def show_panel(self, panel_id): ...
    def show_output_panel(self): ...
    def ensure_panel_zone_visible(self, panel_id): ...
    def activate_panel(self, panel_id): ...
    def activate_view(self, view_id): self.activate_panel(view_id)
    def toggle_bottom_panel(self): ...
    def toggle_figures_dock(self): ...
    def on_figure_ready(self, path): ...
    def on_panel_moved(self, panel_id, zone): ...
    def auto_adjust_zones(self): ...
    def sync_zone_actions(self): ...

    # --- 图标 ---
    def icon_for_key(self, key): ...
    def refresh_sidebar_icons(self): ...

    # --- 外观访问器（供设置页/菜单使用）---
    def is_primary_sidebar(self): ...
    def set_primary_sidebar(self, on): ...
    # ... figures / secondary / panel / view_visible 同理

    # --- 恢复 ---
    def restore_appearance(self): ...   # 仅栏位与可见性
    def restore_splitter_sizes(self): ...  # 原 _restore_layout
```

命名调整：迁出后方法**去掉前导下划线**（从「MainWindow 私有方法」变为「控制器的公共方法」），`is_*`/`set_*` 保留原名。

## 3.4 MainWindow 改造点

1. `__init__` 中在 `_setup_layout()` 之后创建 `self.layout = LayoutManager(self)`。
2. `_setup_layout` 内的面板注册块（`dock.register_panel(...)` 一连串调用）替换为构造一个 spec 列表后调用 `self.layout.register_panels(spec)`。
3. `_connect_signals` 中 `self.dock.panel_moved.connect(self._on_panel_moved)` 改为 `connect(self.layout.on_panel_moved)`。
4. `_restore_appearance` / `_restore_layout` 调用改为 `self.layout.restore_appearance()` / `self.layout.restore_splitter_sizes()`。
5. 删除 3.2 表中所有方法。

## 3.5 调用点修改表（外部 + 内部）

凡是调用 3.2 中方法的地方，都要改指到 `self.layout.*` / `self._mw.layout.*`：

| 调用方文件 | 原调用 | 改为 |
|-----------|--------|------|
| `run_controller.py`（多处） | `self._mw._show_panel(id)` | `self._mw.layout.show_panel(id)` |
| `menu_builder.py` `_add_zone_toggle` | `self._mw.is_primary_sidebar` / `set_primary_sidebar` / `is_secondary_sidebar` / `set_secondary_sidebar` / `is_panel` / `set_panel` | 同名方法改走 `self._mw.layout.*` |
| `settings_panel.py` `_appearance_card` | `mw.is_primary_sidebar` / `mw.set_primary_sidebar` / `is_figures_dock` / `set_figures_dock` / `is_panel` / `set_panel` / `is_view_visible` / `set_view_visible` | 改走 `mw.layout.*`（`is_menu_bar`/`is_status_bar` 不变） |
| `main_window.py` 内部 | `self._show_panel` / `self._is_zone_visible` / `self._set_zone_visible` / `self._ensure_panel_zone_visible` / `self._auto_adjust_zones` / `self._sync_zone_actions` / `self._activate_panel` / `self._on_figure_ready` / `self._refresh_sidebar_icons` 等 | 改走 `self.layout.*` |

> **可选过渡策略**：为降低风险，可在 MainWindow 上保留同名转发属性（`def _show_panel(self, p): return self.layout.show_panel(p)`），验证通过后再删除。建议直接改，因调用点已全部列出。

## 3.6 验证

1. `python -m py_compile` 全部 `ide/*.py`。
2. Headless 冒烟（与第 2 步同款）：
   ```powershell
   $env:QT_QPA_PLATFORM="offscreen"
   python -c "from PyQt5.QtWidgets import QApplication; app=QApplication([]); \
     from npworks_ide.ide.main_window import MainWindow; w=MainWindow(); \
     print(type(w.layout).__name__); w.layout.show_panel('output'); \
     print(w.layout.is_zone_visible('left')); print('OK')"
   ```
3. 手动启动 IDE，验证：拖拽面板停靠、视图菜单栏位勾选、设置页外观开关、首次启动布局恢复。

## 3.7 风险与回滚

- **风险**：`_zone_actions` 字典被菜单构建与 LayoutManager 共享读写；需保证两者引用**同一个 dict 对象**（LayoutManager 持有 `main_window._zone_actions` 引用即可，不要复制）。
- **回滚**：单次 commit 完成第 3 步，`git revert` 即可整体回退。

---

# 第 4 步：按功能域分子包

## 4.1 目标

把 `ide/` 下 35 个平铺模块按功能域归入子包，降低认知负担、明确依赖方向。

## 4.2 目标目录结构

```
src/npworks_ide/
├── __init__.py
├── __main__.py
├── app.py                       # 入口（不动）
├── runner/
│   ├── __init__.py
│   └── executor.py
└── ide/
    ├── __init__.py              # 过渡 shim（见 4.5），最终清空
    ├── workbench/               # 主框架装配
    │   ├── main_window.py
    │   ├── menu_builder.py
    │   └── layout_manager.py    # 第 3 步产物
    ├── controllers/             # 业务控制器
    │   ├── actions.py
    │   ├── run_controller.py
    │   ├── find_controller.py
    │   ├── edit_controller.py
    │   ├── theme_controller.py
    │   ├── command_registry.py
    │   ├── env_controller.py
    │   ├── env_manager.py       # 由 venv_manager.py 改名
    │   └── env_dialogs.py       # 由 venv_dialogs.py 改名
    ├── widgets/                 # 可复用控件
    │   ├── editor.py
    │   ├── find_replace.py
    │   ├── output_panel.py
    │   ├── terminal.py
    │   ├── shell_terminal.py
    │   ├── figures_view.py
    │   ├── activity_bar.py
    │   ├── window_controls.py
    │   └── preview_image.py
    ├── panels/                  # 面板/视图
    │   ├── settings_panel.py
    │   ├── plugins_panel.py
    │   ├── command_palette.py
    │   ├── explorer_view.py
    │   └── file_tree.py
    ├── dock/                    # 停靠系统
    │   ├── dock_manager.py
    │   └── document_panel.py
    ├── plugin/                  # 插件系统
    │   ├── plugin_api.py
    │   ├── plugin_loader.py
    │   ├── builtin_editors.py
    │   └── editor_registry.py
    ├── platform/                # 平台相关
    │   ├── native_window.py
    │   └── icons.py
    └── themes/                  # （已存在，保持不动）
        ├── __init__.py
        ├── palette.py
        ├── variables.py
        └── template.qss
```

## 4.3 文件迁移映射表

| 当前路径 | 目标路径 | 改名 |
|---------|---------|------|
| `ide/main_window.py` | `ide/workbench/main_window.py` | |
| `ide/menu_builder.py` | `ide/workbench/menu_builder.py` | |
| `ide/actions.py` | `ide/controllers/actions.py` | |
| `ide/run_controller.py` | `ide/controllers/run_controller.py` | |
| `ide/find_controller.py` | `ide/controllers/find_controller.py` | |
| `ide/edit_controller.py` | `ide/controllers/edit_controller.py` | |
| `ide/theme_controller.py` | `ide/controllers/theme_controller.py` | |
| `ide/command_registry.py` | `ide/controllers/command_registry.py` | |
| `ide/env_controller.py` | `ide/controllers/env_controller.py` | |
| `ide/venv_manager.py` | `ide/controllers/env_manager.py` | **重命名** |
| `ide/venv_dialogs.py` | `ide/controllers/env_dialogs.py` | **重命名** |
| `ide/editor.py` | `ide/widgets/editor.py` | |
| `ide/find_replace.py` | `ide/widgets/find_replace.py` | |
| `ide/output_panel.py` | `ide/widgets/output_panel.py` | |
| `ide/terminal.py` | `ide/widgets/terminal.py` | |
| `ide/shell_terminal.py` | `ide/widgets/shell_terminal.py` | |
| `ide/figures_view.py` | `ide/widgets/figures_view.py` | |
| `ide/activity_bar.py` | `ide/widgets/activity_bar.py` | |
| `ide/window_controls.py` | `ide/widgets/window_controls.py` | |
| `ide/preview_image.py` | `ide/widgets/preview_image.py` | |
| `ide/settings_panel.py` | `ide/panels/settings_panel.py` | |
| `ide/plugins_panel.py` | `ide/panels/plugins_panel.py` | |
| `ide/command_palette.py` | `ide/panels/command_palette.py` | |
| `ide/explorer_view.py` | `ide/panels/explorer_view.py` | |
| `ide/file_tree.py` | `ide/panels/file_tree.py` | |
| `ide/dock_manager.py` | `ide/dock/dock_manager.py` | |
| `ide/document_panel.py` | `ide/dock/document_panel.py` | |
| `ide/plugin_api.py` | `ide/plugin/plugin_api.py` | |
| `ide/plugin_loader.py` | `ide/plugin/plugin_loader.py` | |
| `ide/builtin_editors.py` | `ide/plugin/builtin_editors.py` | |
| `ide/editor_registry.py` | `ide/plugin/editor_registry.py` | |
| `ide/native_window.py` | `ide/platform/native_window.py` | |
| `ide/icons.py` | `ide/platform/icons.py` | |

## 4.4 import 改写规则

仓库内全部使用绝对导入 `npworks_ide.ide.<mod>`。迁移后需把：

```
npworks_ide.ide.<mod>      →  npworks_ide.ide.<子包>.<mod>
from npworks_ide.ide import <mod>  →  from npworks_ide.ide.<子包> import <mod>
```

**重命名模块**另需：
```
npworks_ide.ide.venv_manager   →  npworks_ide.ide.controllers.env_manager
npworks_ide.ide.venv_dialogs   →  npworks_ide.ide.controllers.env_dialogs
```

受影响文件范围：`npworks-ide/src/**`、以及插件包 `npworks-plugin-*/src/**`（插件通过 `plugin_api` 间接依赖，需检查是否直接 import 了上述模块）。

## 4.5 过渡 shim（强烈建议，降低风险）

迁移期间在 `ide/__init__.py` 用 re-export 让旧路径仍可用，**使每个批次都能独立通过冒烟测试、且不破坏尚未迁移的代码与插件**：

```python
# ide/__init__.py（迁移期间）
# 过渡兼容层：旧导入路径 npworks_ide.ide.<mod> 仍可用。
# 全部批次完成后删除本文件内容（保留为空 __init__）。
from npworks_ide.ide.platform import icons, native_window          # noqa
from npworks_ide.ide.dock import dock_manager, document_panel       # noqa
from npworks_ide.ide.widgets import (editor, find_replace, ...)     # noqa
from npworks_ide.ide.controllers import (...)                       # noqa
from npworks_ide.ide.panels import (...)                            # noqa
from npworks_ide.ide.plugin import (...)                            # noqa
# 重命名兼容
from npworks_ide.ide.controllers import env_manager as venv_manager  # noqa
from npworks_ide.ide.controllers import env_dialogs as venv_dialogs  # noqa
```

> 原理：`from npworks_ide.ide.<mod> import X` 在 `ide/<mod>.py` 不存在时，会回退到 `ide/__init__.py` 中由 re-export 注入的属性 `<mod>`，从而解析成功。每完成一个批次的「文件迁移 + 内部 import 改写」后，shim 中对应行即可保留（仍指向新位置），最终统一删除。

## 4.6 分批迁移顺序（每批一次 commit）

按「被依赖多 → 少」的反序，先迁叶子模块：

| 批次 | 子包 | 模块 | 说明 |
|------|------|------|------|
| **A** | `platform/` | `native_window`, `icons` | `icons` 被广泛导入，迁完即更新其所有 importer（通过 shim 兜底） |
| **B** | `dock/` | `dock_manager`, `document_panel` | |
| **C** | `widgets/` | `editor`, `find_replace`, `output_panel`, `terminal`, `shell_terminal`, `figures_view`, `activity_bar`, `window_controls`, `preview_image` | 本批模块数最多，建议再细分 C1/C2 |
| **D** | `controllers/` | `actions`, `run_controller`, `find_controller`, `edit_controller`, `theme_controller`, `command_registry`, `env_controller`, `env_manager`(改名), `env_dialogs`(改名) | 含 2 个重命名 |
| **E** | `panels/` | `settings_panel`, `plugins_panel`, `command_palette`, `explorer_view`, `file_tree` | |
| **F** | `plugin/` | `plugin_api`, `plugin_loader`, `builtin_editors`, `editor_registry` | 注意：外部插件包可能直接 import 这些 |
| **G** | `workbench/` | `main_window`, `menu_builder`（+ 第 3 步的 `layout_manager`） | 最后迁，依赖前面所有 |
| **收尾** | — | 清空 `ide/__init__.py` 的 shim；删除死文件 `bottom_panel.py`/`outline_view.py`/`sidebar_panel.py`/`theme.py` | |

**每个批次的标准动作**：
1. `git mv` 移动文件（保留 git 历史）。
2. 改写被迁模块**自身**的内部 import（如它 import 了同批或已迁模块）。
3. 更新 `ide/__init__.py` 的 shim 对应行。
4. 运行 4.7 验证。
5. `git commit`。

## 4.7 验证

每批结束后执行：

```powershell
# 1. 全量编译
python -m compileall -q src/npworks_ide
# 2. 导入图自检：确保没有残留旧路径导入
Select-String -Path src\**\*.py -Pattern "npworks_ide\.ide\.venv_manager|npworks_ide\.ide\.editor\b"  # 举例
# 3. Headless 冒烟（同 3.6）
$env:QT_QPA_PLATFORM="offscreen"
python -c "from PyQt5.QtWidgets import QApplication; app=QApplication([]); \
  from npworks_ide.ide.main_window import MainWindow; MainWindow(); print('OK')"
# 4. 插件加载冒烟（确保外部插件包仍可用）
```

收尾（删 shim 后）追加一次**全量旧路径搜索**，确认无任何 `npworks_ide.ide.<mod>`（无子包）形式的导入残留。

## 4.8 跨平台与插件兼容

- **跨平台**：本步纯文件移动 + import 改写，不涉及运行时逻辑，Windows/Ubuntu 行为一致。
- **插件包**：`npworks-plugin-csv/markdown/pdf` 可能直接 `from npworks_ide.ide.plugin_api import ...` 或更深的路径。**批次 F** 前先 grep 三个插件包的 import；若插件用了深路径，要么更新插件，要么依赖 `ide/__init__.py` shim 兜底（推荐后者，shim 在收尾前一直保留）。
- **pyproject 入口点**：`pyproject.toml` 的 `npworks-ide = "npworks_ide.app:main"` 不受影响（`app.py` 位置不变）。

## 4.9 风险与回滚

- **风险**：import 改写遗漏 → 启动时 `ImportError`。缓解：shim 兜底 + 每批冒烟 + 收尾全量搜索。
- **风险**：`git mv` 后 Windows 文件锁（前述 `bottom_panel` 同类问题）导致移动失败。缓解：确保 IDE/编辑器关闭这些文件后再操作；失败时改用「新建+复制+删除」。
- **回滚**：每批独立 commit，可逐批 `git revert`。

---

## 完成定义（Definition of Done）

- [ ] 第 3 步：`main_window.py` ≤ 650 行；`layout_manager.py` 存在且通过冒烟；调用点全部改走 `self.layout.*`。
- [ ] 第 4 步：`ide/` 下不再有平铺的业务模块（仅保留 `__init__.py` 与子包目录）；`ide/__init__.py` shim 已清空；全量旧路径搜索无残留；IDE 与三个插件包均能正常加载。
- [ ] 死文件 `bottom_panel.py`/`outline_view.py`/`sidebar_panel.py`/`theme.py` 已物理删除。
- [ ] Windows 与 Ubuntu 下均能启动并运行用户代码。

---

## 建议执行节奏

1. 先单独做**第 3 步**（1 个 commit，约 1–2 小时，风险低）。
2. 第 3 步稳定后，再开**第 4 步**，按 A→G 逐批提交，每批都保证可启动。
3. 全部完成后删除 shim 与死文件，做一次端到端回归（含插件）。
