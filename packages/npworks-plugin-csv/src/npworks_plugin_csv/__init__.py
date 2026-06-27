"""npworks 示例插件：CSV/TSV 表格查看器。

通过入口点 npworks.plugins 注册：pip install 本包后，npworks 启动时自动发现
并加载，.csv/.tsv 文件即在编辑区以表格视图打开。
"""
from .csv_view import CsvView, CsvProvider

__version__ = "0.0.1"


def register(api):
    api.register_editor(CsvProvider())
