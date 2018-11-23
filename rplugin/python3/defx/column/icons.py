# ============================================================================
# FILE: icons.py
# AUTHOR: Kristijan Husak <husakkristijan at gmail.com>
# License: MIT license
# ============================================================================

import re
from pathlib import Path
from defx.base.column import Base
from defx.context import Context
from neovim import Nvim


class Column(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = 'icons'
        self.opts = self.vim.call('defx_icons#get')

    def get(self, context: Context, candidate: dict) -> str:
        path: Path = candidate['action__path']
        if 'mark' not in context.columns and candidate['is_selected']:
            return self.icon(self.opts['mark_icon'])

        if candidate.get('is_root', False):
            return self.icon(self.opts['parent_icon'])

        if candidate['is_directory']:
            if path.is_symlink():
                return self.icon(self.opts['directory_symlink_icon'])

            return self.icon(self.opts['directory_icon'])

        ext = path.suffix[1:].lower()
        filename = path.name.lower()

        for pattern, pattern_data in self.opts['pattern_matches'].items():
            if re.search(pattern, filename) is not None:
                return self.icon(pattern_data['icon'])

        if filename in self.opts['exact_matches']:
            return self.icon(self.opts['exact_matches'][filename]['icon'])

        if ext in self.opts['extensions']:
            return self.icon(self.opts['extensions'][ext]['icon'])

        return self.icon(self.opts['default_icon'])

    def length(self, context: Context) -> int:
        return self.opts['column_length']

    def icon(self, icon: str) -> str:
        return format(icon, f'<{self.opts["column_length"]}')

    def highlight(self) -> None:
        self.vim.command((
            'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
        ).format(self.syntax_name, 'icon_mark', self.opts['mark_icon']))
        self.vim.command('highlight default link {0}_{1} Statement'.format(
            self.syntax_name, 'icon_mark'
        ))

        if not self.opts['enable_syntax_highlight']:
            return

        self.vim.command((
            'syntax match {0}_{1} /[{2}]/ contained containedin={0}').format(
                self.syntax_name, 'directory', self.opts['directory_icon']
            ))
        self.vim.command('highlight default link {0}_{1} Directory'.format(
            self.syntax_name, 'directory'
        ))

        self.vim.command((
            'syntax match {0}_{1} /[{2}]/ contained containedin={0}').format(
                self.syntax_name, 'parent_directory', self.opts['parent_icon']
            ))
        self.vim.command('highlight default link {0}_{1} Directory'.format(
            self.syntax_name, 'parent_directory'
        ))

        self.vim.command((
            'syntax match {0}_{1} /[{2}]/ contained containedin={0}').format(
                self.syntax_name, 'symlink_directory',
                self.opts['directory_symlink_icon']
            ))
        self.vim.command('highlight default link {0}_{1} Directory'.format(
            self.syntax_name, 'symlink_directory'
        ))

        for pattern, pattern_data in self.opts['pattern_matches'].items():
            pattern_text = re.sub('[^A-Za-z]', '', pattern)
            self.vim.command((
                'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
            ).format(self.syntax_name, pattern_text, pattern_data['icon']))
            self.vim.command('highlight default {0}_{1} guifg=#{2}'.format(
                self.syntax_name, pattern_text, pattern_data['color']))

        for exact_file, exact_match_data in self.opts['exact_matches'].items():
            file_text = re.sub('[^A-Za-z]', '', exact_file)
            self.vim.command((
                'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
            ).format(self.syntax_name, file_text, exact_match_data['icon']))
            self.vim.command('highlight default {0}_{1} guifg=#{2}'.format(
                self.syntax_name, file_text, exact_match_data['color']))

        for ext, ext_data in self.opts['extensions'].items():
            self.vim.command((
                'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
            ).format(self.syntax_name, ext, ext_data['icon']))
            self.vim.command('highlight default {0}_{1} guifg=#{2}'.format(
                self.syntax_name, ext, ext_data['color']
            ))
