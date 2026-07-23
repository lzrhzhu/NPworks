"""
Runner for npworks-content scripts.

Provides a CLI that runs chapter scripts with plt.show() monkey-patched
to save figures instead of displaying them.

Filename convention:
    Each figure must have a suptitle set via fig.suptitle("stem_name")
    or plt.suptitle("stem_name"). The runner derives the output filename
    as: <chapter_id>_<stem_name>.png

Usage:
    python -m npworks_content.runner run ch02 /path/to/images
    python -m npworks_content.runner run ch02 /path/to/images 01_bicycle_no_drag.py
"""
import os
import re
import sys
import importlib


def _sanitize(text):
    text = text.strip()
    text = re.sub(r'[^\w\u4e00-\u9fff-]', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_')


def run_script(script_path, save_dir, chapter_id):
    """
    Execute a standalone script with plt.show() patched to save figures.

    Figures are saved as <save_dir>/<chapter_id>_<suptitle>.png.
    The suptitle is read from fig._suptitle (set by plt.suptitle / fig.suptitle).
    If no suptitle is set, falls back to the first axes title, then to fig_N.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # 让图中中文标签正常显示（默认 DejaVu Sans 不含 CJK 字形）。
    # 这里把一族中文字体设为首选回退；找不到时仍回退到默认无衬线字体。
    from matplotlib import font_manager
    _cjk_candidates = ["Microsoft YaHei", "SimHei", "Noto Sans SC", "Source Han Sans SC",
                       "PingFang SC", "WenQuanYi Zen Hei", "Arial Unicode MS"]
    _available = {f.name for f in font_manager.fontManager.ttflist}
    _cjk = [n for n in _cjk_candidates if n in _available]
    if _cjk:
        plt.rcParams["font.sans-serif"] = _cjk + plt.rcParams.get("font.sans-serif", [])
        plt.rcParams["axes.unicode_minus"] = False

    os.makedirs(save_dir, exist_ok=True)

    counter = [0]

    original_show = plt.show

    def _show_replacement(*args, **kwargs):
        for fig_num in list(plt.get_fignums()):
            fig = plt.figure(fig_num)
            counter[0] += 1

            stem = ''
            if fig._suptitle is not None and fig._suptitle.get_text():
                stem = _sanitize(fig._suptitle.get_text())
            elif fig.axes and fig.axes[0].get_title():
                stem = _sanitize(fig.axes[0].get_title())

            if stem:
                filename = f"{chapter_id}_{stem}.png"
            else:
                filename = f"{chapter_id}_fig_{counter[0]}.png"

            path = os.path.join(save_dir, filename)

            # 为 suptitle 预留顶部空间，避免总标题与子图/坐标轴重叠。
            # tight_layout(rect=...) 会把坐标轴限制在 [0, 0.93] 区域内，
            # suptitle（默认 y≈0.98）落在预留的顶部边距中，从而留出清晰间距。
            has_suptitle = (fig._suptitle is not None
                            and fig._suptitle.get_text())
            if has_suptitle:
                try:
                    fig.tight_layout(rect=[0, 0, 1, 0.92])
                except Exception:
                    try:
                        fig.subplots_adjust(top=0.88)
                    except Exception:
                        pass

            fig.savefig(path, dpi=150, bbox_inches='tight')
            print(f"Saved: {path}")
            plt.close(fig)

    plt.show = _show_replacement

    import types
    module = types.ModuleType('__main__')
    module.__file__ = script_path
    module.__name__ = '__main__'

    with open(script_path, encoding='utf-8') as f:
        code = f.read()

    sys.modules['__main__'] = module
    exec(compile(code, script_path, 'exec'), module.__dict__)

    plt.show = original_show


def main():
    if len(sys.argv) < 4 or sys.argv[1] != 'run':
        print("Usage: python -m npworks_content.runner run <chapter_id> <save_dir> [script_name]")
        sys.exit(1)

    chapter_id = sys.argv[2]
    save_dir = sys.argv[3]

    if len(sys.argv) >= 5:
        script_name = sys.argv[4]
    else:
        script_name = None

    from npworks_content.loader import ContentLoader
    loader = ContentLoader()
    chapter_path = loader.get_section_path(chapter_id, '')

    if not chapter_path or not os.path.isdir(chapter_path):
        print(f"Chapter not found: {chapter_id}")
        sys.exit(1)

    scripts = sorted(f for f in os.listdir(chapter_path) if f.endswith('.py'))
    if script_name:
        scripts = [s for s in scripts if s == script_name]

    for script in scripts:
        script_path = os.path.join(chapter_path, script)
        print(f"Running: {script}")
        try:
            run_script(script_path, save_dir, chapter_id)
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == '__main__':
    main()
