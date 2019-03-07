# Defx icons

Custom implementation of [vim-devicons](https://github.com/ryanoasis/vim-devicons) for [defx.nvim](https://github.com/Shougo/defx.nvim).

![screenshot from 2018-11-22 23-39-41](https://user-images.githubusercontent.com/1782860/48923552-eeed0b80-eeaf-11e8-98e8-8f4e7ec85194.png)

## Usage
```vimL
:Defx -columns=icons:filename:type
```
This column is a replacement for mark column. It will properly highlight selected files.

## Configuration
This is the default configuration:

```vimL
let g:defx_icons_enable_syntax_highlight = 1
let g:defx_icons_column_length = 2
let g:defx_icons_directory_icon = ''
let g:defx_icons_mark_icon = '*'
let g:defx_icons_parent_icon = ''
let g:defx_icons_default_icon = ''
let g:defx_icons_directory_symlink_icon = ''
" Options below are applicable only when using "tree" feature
let g:defx_icons_root_opened_tree_icon = ''
let g:defx_icons_nested_opened_tree_icon = ''
let g:defx_icons_nested_closed_tree_icon = ''
```

Note: Syntax highlighting can cause some performance issues in defx window. Just disable it with the `let g:defx_icons_enable_syntax_highlight = 0`

## Thanks to

* [vim-devicons](https://github.com/ryanoasis/vim-devicons) for icons
* [vim-nerdtree-syntax-highlight](https://github.com/tiagofumo/vim-nerdtree-syntax-highlight) for colors
