# docs/source/zh/conf.py
import os
import sys

# 确保 Sphinx 能找到源码（如果需要 autodoc）
sys.path.insert(0, os.path.abspath('../../..'))

project = 'Maze'
copyright = '2025, HUST'
author = 'HUST'

# ✅ 关键：设置语言为中文
language = 'zh_CN'

# 启用的扩展（和英文版保持一致）
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.httpdomain',   # 用于 API 文档
    'sphinx_copybutton',          # 复制按钮
]

# Intersphinx 映射
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# 使用 Read the Docs 主题
html_theme = 'sphinx_rtd_theme'

# 可选：优化主题显示
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

# 输出路径（RTD 自动处理，这里可不设）
# html_output_dir = '_build/html'

# 高亮语言
highlight_language = 'python'

# EPUB 设置
epub_show_urls = 'footnote'