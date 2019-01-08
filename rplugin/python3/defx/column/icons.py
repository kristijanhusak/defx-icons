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
        filename = path.name
        if 'mark' not in context.columns and candidate['is_selected']:
            return self.icon(self.opts['mark_icon'])

        if candidate.get('is_root', False):
            return self.icon(self.opts['parent_icon'])

        if candidate['is_directory']:
            if filename in self.opts['exact_dir_matches']:
                return self.icon(self.opts['exact_dir_matches'][filename]['icon'])

            if path.is_symlink():
                return self.icon(self.opts['directory_symlink_icon'])

            return self.icon(self.opts['directory_icon'])

        filename = filename.lower()
        ext = path.suffix[1:].lower()

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

    def syn_item(self, name, opt_name, hi_group_name) -> None:
        self.vim.command(f'silent! syntax clear {self.syntax_name}_{name}')
        self.vim.command((
            'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
        ).format(self.syntax_name, name, self.opts[opt_name]))
        self.vim.command('highlight default link {0}_{1} {2}'.format(
            self.syntax_name, name, hi_group_name
        ))

    def syn_list(self, opt) -> None:
        for name, opts in self.opts[opt].items():
            text = re.sub('[^A-Za-z]', '', name)
            self.vim.command(f'silent! syntax clear {self.syntax_name}_{text}')
            self.vim.command((
                'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
            ).format(self.syntax_name, text, opts['icon']))
            self.vim.command('highlight default {0}_{1} guifg=#{2}'.format(
                self.syntax_name, text, opts['color']))

    def highlight(self) -> None:
        self.syn_item('icon_mark', 'mark_icon', 'Statement')

        if not self.opts['enable_syntax_highlight']:
            return

        self.syn_item('directory', 'directory_icon', 'Directory')
        self.syn_item('parent_directory', 'parent_icon', 'Directory')
        self.syn_item('symlink_directory', 'directory_symlink_icon', 'Directory')

        self.syn_list('pattern_matches')
        self.syn_list('exact_matches')
        self.syn_list('exact_dir_matches')
        self.syn_list('extensions')
