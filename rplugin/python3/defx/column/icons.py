# ============================================================================
# FILE: icons.py
# AUTHOR: Kristijan Husak <husakkristijan at gmail.com>
# License: MIT license
# ============================================================================

import re
import typing
from pathlib import Path
from defx.base.column import Base, Highlights
from defx.context import Context
from defx.clipboard import ClipboardAction
from defx.view import View
from defx.util import Nvim, Candidate, len_bytes


class Column(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)
        self.vim = vim
        self.name = 'icons'
        self.has_get_with_highlights = True
        self.opts = self.vim.call('defx_icons#get')
        self.icons = self.opts['icons']
        self.settings = self.opts['settings']
        self.highlights: typing.Dict[str, typing.Any] = {}
        self.generate_highlights_map()

    def item_hl(self, name, hi_group) -> None:
        icon = format(self.icons[name], f'<{self.settings["column_length"]}')
        self.highlights[name] = (
            icon,
            hi_group,
            len_bytes(icon)
        )

    def list_hl(self, list_name) -> None:
        self.highlights[list_name] = {}
        for name, opts in self.icons[list_name].items():
            text = re.sub('[^A-Za-z]', '', name)
            icon = format(opts['icon'], f'<{self.settings["column_length"]}')
            self.highlights[list_name][name] = (
                icon,
                f'{self.syntax_name}_{text}',
                len_bytes(icon)
            )

    def generate_highlights_map(self) -> None:
        self.item_hl('default_icon', '')
        self.item_hl('mark_icon', 'DefxIconsMarkIcon')
        self.item_hl('copy_icon', 'DefxIconsCopyIcon')
        self.item_hl('move_icon', 'DefxIconsMoveIcon')
        self.item_hl('directory_icon', 'DefxIconsDirectory')
        self.item_hl('parent_icon', 'DefxIconsParentDirectory')
        self.item_hl('directory_symlink_icon', 'DefxIconsSymlinkDirectory')
        self.item_hl('root_opened_tree_icon', 'DefxIconsOpenedTreeIcon')
        self.item_hl('nested_opened_tree_icon', 'DefxIconsNestedTreeIcon')
        self.item_hl('nested_closed_tree_icon', 'DefxIconsClosedTreeIcon')

        self.list_hl('pattern_matches')
        self.list_hl('exact_matches')
        self.list_hl('exact_dir_matches')
        self.list_hl('extensions')

    def on_init(self, view: View, context: Context) -> None:
        self._context = context
        self._view = view
        for cmd in self.get_highlight_commands(True):
            self.vim.command(cmd)

    def on_redraw(self, view: View, context: Context) -> None:
        self._context = context
        self._view = view

    def get_with_highlights(
        self, context: Context, candidate: Candidate
    ) -> typing.Tuple[str, Highlights]:
        path: Path = candidate['action__path']
        filename = path.name
        if 'mark' not in context.columns and candidate['is_selected']:
            return self.icon('mark_icon')

        if self._view and self._view._clipboard.candidates:
            for clipboard_candidate in self._view._clipboard.candidates:
                if str(clipboard_candidate['action__path']) == str(path):
                    return self.clipboard_icon()

        if candidate.get('is_root', False):
            return self.icon('parent_icon')

        if candidate['is_directory']:
            if filename in self.icons['exact_dir_matches']:
                return self.icon('exact_dir_matches', filename)

            if candidate.get('level', 0) > 0:
                if candidate.get('is_opened_tree'):
                    return self.icon('nested_opened_tree_icon')
                return self.icon('nested_closed_tree_icon')

            if candidate.get('is_opened_tree', False):
                return self.icon('root_opened_tree_icon')

            if path.is_symlink():
                return self.icon('directory_symlink_icon')

            return self.icon('directory_icon')

        filename = filename.lower()
        ext = path.suffix[1:].lower()

        for pattern, pattern_data in self.icons['pattern_matches'].items():
            if re.search(pattern, filename) is not None:
                return self.icon('pattern_matches', pattern)

        if filename in self.icons['exact_matches']:
            return self.icon('exact_matches', filename)

        if ext in self.icons['extensions']:
            return self.icon('extensions', ext)

        return self.icon('default_icon')

    def icon(
        self, icon_name, nested_icon_name = None
    ) -> typing.Tuple[str, Highlights]:
        icon = self.highlights[icon_name]
        if nested_icon_name is not None:
            icon = icon[nested_icon_name]
        return (icon[0], [(icon[1], self.start, icon[2])])

    def length(self, context: Context) -> int:
        return typing.cast(int, self.settings['column_length'])

    def clipboard_icon(self) -> str:
        if  self._view._clipboard.action == ClipboardAction.COPY:
            return self.icon('copy_icon')
        if self._view._clipboard.action == ClipboardAction.MOVE:
            return self.icon('move_icon')
        return ''

    def syn_item(self, name, opt_name, hi_group_name, from_init = False) -> typing.List[str]:
        commands: typing.List[str] = []
        if not from_init:
            commands.append(f'silent! syntax clear {self.syntax_name}_{name}')
            commands.append((
                'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
            ).format(self.syntax_name, name, self.icons[opt_name]))
        commands.append('highlight default link {0}_{1} {2}'.format(
            self.syntax_name, name, hi_group_name
        ))
        return commands

    def syn_list(self, opt, from_init = False) -> typing.List[str]:
        commands: typing.List[str] = []
        for name, opts in self.icons[opt].items():
            text = re.sub('[^A-Za-z]', '', name)
            if not from_init:
                commands.append(f'silent! syntax clear {self.syntax_name}_{text}')
                commands.append((
                    'syntax match {0}_{1} /[{2}]/ contained containedin={0}'
                ).format(self.syntax_name, text, opts['icon']))
            commands.append('highlight default {0}_{1} guifg=#{2} ctermfg={3}'.format(
                self.syntax_name, text, opts['color'], opts.get('term_color',
                                                                'NONE')))
        return commands

    def highlight_commands(self) -> typing.List[str]:
        return self.get_highlight_commands()

    def get_highlight_commands(self, from_init = False) -> typing.List[str]:
        commands: typing.List[str] = []

        if not self.settings['enable_syntax_highlight']:
            return commands

        commands += self.syn_item('icon_mark', 'mark_icon', 'DefxIconsMarkIcon', from_init)
        commands += self.syn_item('icon_copy', 'copy_icon', 'DefxIconsCopyIcon', from_init)
        commands += self.syn_item('icon_move', 'move_icon', 'DefxIconsMoveIcon', from_init)

        commands += self.syn_item('directory', 'directory_icon', 'DefxIconsDirectory', from_init)
        commands += self.syn_item('parent_directory', 'parent_icon', 'DefxIconsParentDirectory', from_init)
        commands += self.syn_item('symlink_directory', 'directory_symlink_icon', 'DefxIconsSymlinkDirectory', from_init)
        commands += self.syn_item('root_opened_tree_icon', 'root_opened_tree_icon', 'DefxIconsOpenedTreeIcon', from_init)
        commands += self.syn_item('nested_opened_tree_icon', 'nested_opened_tree_icon', 'DefxIconsNestedTreeIcon', from_init)
        commands += self.syn_item('nested_closed_tree_icon', 'nested_closed_tree_icon', 'DefxIconsClosedTreeIcon', from_init)

        commands += self.syn_list('pattern_matches', from_init)
        commands += self.syn_list('exact_matches', from_init)
        commands += self.syn_list('exact_dir_matches', from_init)
        commands += self.syn_list('extensions', from_init)

        return commands
