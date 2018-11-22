# Defx icons

Custom implementation of [vim-devicons](https://github.com/ryanoasis/vim-devicons) for [defx.nvim](https://github.com/Shougo/defx.nvim).


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
```

Note: Syntax highlighting can cause some performance issues in defx window. Just disable it with the `let g:defx_icons_enable_syntax_highlight = 0`
