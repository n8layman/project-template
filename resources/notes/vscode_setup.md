
To run R in vscode on an arm64 mac several steps must be taken

## Radian
1. Install ncurses: `brew install ncurses`
2. Install python using pyenv: `brew install pyenv`
3. Install python build dependencies: `brew install openssl readline sqlite3 xz zlib`
4. Install python3 using pyenv: `pyenv install 3.12` (or most recent version)
5. Install pipx: `brew install pipx`
6. Install radian using pipx: `pipx install radian`
7. Update VScode to use radian terminal. Add:
 `{
"r.rterm.mac": "/usr/local/bin/radian"
}`
to the VScode settings json. Open settings json via

Troubleshooting:
    1. zsh: /opt/homebrew/bin/radian: bad interpreter: /opt/homebrew/opt/python@3.10/bin/python3.10: no such file or directory. Solution was to `rm -rf /opt/homebrew/bin/radian` and re-install via pipx `pipx install radian`
