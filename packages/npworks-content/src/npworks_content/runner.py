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
