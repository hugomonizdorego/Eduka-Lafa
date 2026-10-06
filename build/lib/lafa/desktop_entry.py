"""freedesktop Exec quoting: string escaping followed by argument quoting."""

def exec_path(path):
    text=str(path)
    if not text or '=' in text or any(ord(character)<32 for character in text):raise ValueError('The executable path contains characters unsupported by desktop entries.')
    # Quote the argument, then encode the desktop string value. A literal
    # backslash needs four backslashes; a dollar sign needs two before it.
    quoted='"'+''.join('\\'+character if character in {'"','`','$','\\'} else character for character in text)+'"'
    return quoted.replace('\\','\\\\').replace('%','%%')
