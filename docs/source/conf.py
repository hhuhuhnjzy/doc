# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'Maze'
copyright = '2025, HUST'
author = 'HUST'
release = '0.1'
version = '0.1.0'
language='zh_CN'
# -- General configuration ---------------------------------------------------

# Add necessary extensions
extensions = [
    'sphinx.ext.internationalization',
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',        # 可选：添加源码链接
    'sphinxcontrib.httpdomain',   # ✅ 关键：支持 .. http:get:: 等指令
    'sphinx_copybutton',          # 可选：为代码块添加复制按钮（推荐）
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

# Optional: configure sphinx_rtd_theme
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

# -- Options for EPUB output -------------------------------------------------
epub_show_urls = 'footnote'

# -- Additional settings -----------------------------------------------------
# Ensure JSON is highlighted properly
highlight_language = 'python'

# Suppress warnings for missing references (optional)
suppress_warnings = ['ref.citation']