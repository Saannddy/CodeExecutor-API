import re
from typing import List, Tuple

def _compile(patterns: List[Tuple[str, str]]):
    return [(re.compile(p, re.IGNORECASE | re.MULTILINE), reason) for p, reason in patterns]


# ── Python ────────────────────────────────────────────────────────────────────
_PYTHON_PATTERNS = _compile([
    # Process / shell
    (r'\bos\s*\.\s*(system|popen|exec[lv]?[pe]?)\b',    'os.system / os.popen — shell execution'),
    (r'\bsubprocess\b',                                   'subprocess — process spawning'),
    (r'\bcommands\b',                                     'commands module — legacy shell execution'),

    # File system
    (r'\bopen\s*\(',                                      'open() — file system access'),
    (r'\bos\s*\.\s*(remove|unlink|rmdir|rename|makedirs|mkdir|listdir|walk|scandir|chmod|chown)\b',
                                                          'os file operations'),
    (r'\bshutil\b',                                       'shutil — file/directory manipulation'),
    (r'\bpathlib\b',                                      'pathlib — file system access'),
    (r'\b__builtins__\b',                                 '__builtins__ — built-in manipulation'),

    # Network
    (r'\bsocket\b',                                       'socket — raw network access'),
    (r'\burllib\b',                                       'urllib — HTTP requests'),
    (r'\brequests\b',                                     'requests — HTTP library'),
    (r'\bhttp\s*\.\s*client\b',                           'http.client — HTTP requests'),
    (r'\bftplib\b',                                       'ftplib — FTP access'),
    (r'\bsmtplib\b',                                      'smtplib — email sending'),

    # Dynamic code
    (r'\beval\s*\(',                                      'eval() — arbitrary code execution'),
    (r'\bexec\s*\(',                                      'exec() — arbitrary code execution'),
    (r'\bcompile\s*\(',                                   'compile() — dynamic compilation'),
    (r'\b__import__\s*\(',                                '__import__() — dynamic module loading'),
    (r'\bimportlib\b',                                    'importlib — dynamic imports'),
    (r'\bctypes\b',                                       'ctypes — C-level access'),

    # Environment / introspection
    (r'\bos\s*\.\s*environ\b',                            'os.environ — environment variable access'),
    (r'\bos\s*\.\s*getenv\b',                             'os.getenv — environment variable access'),
    (r'/etc/passwd',                                      '/etc/passwd — system file access'),
    (r'/proc/',                                           '/proc/ — process introspection'),
    (r'\bsignal\b',                                       'signal — signal handling'),
    (r'\bglobals\s*\(\)',                                  'globals() — scope introspection'),
])


# ── JavaScript / Node.js ──────────────────────────────────────────────────────
_JS_PATTERNS = _compile([
    # Process / shell
    (r'\bchild_process\b',                                'child_process — shell execution'),
    (r'\bexecSync\b',                                     'execSync — shell execution'),
    (r'\bspawnSync\b',                                    'spawnSync — process spawning'),
    (r'\bprocess\s*\.\s*exit\b',                          'process.exit — forced exit'),
    (r'\bprocess\s*\.\s*env\b',                           'process.env — environment access'),
    (r'\bprocess\s*\.\s*kill\b',                          'process.kill — process killing'),

    # File system
    (r"\brequire\s*\(\s*['\"]fs['\"]\s*\)",               'require("fs") — file system access'),
    (r'\bfs\s*\.\s*(readFile|writeFile|unlink|rmdir|mkdir|readdir|rename|chmod)\b',
                                                          'fs operations — file manipulation'),

    # Network
    (r"\brequire\s*\(\s*['\"]net['\"]\s*\)",              'require("net") — raw sockets'),
    (r"\brequire\s*\(\s*['\"]http['\"]\s*\)",             'require("http") — HTTP server/client'),
    (r"\brequire\s*\(\s*['\"]https['\"]\s*\)",            'require("https") — HTTPS access'),
    (r"\brequire\s*\(\s*['\"]dgram['\"]\s*\)",            'require("dgram") — UDP sockets'),
    (r'\bfetch\s*\(',                                     'fetch() — network requests'),
    (r'\bXMLHttpRequest\b',                               'XMLHttpRequest — HTTP requests'),

    # Dynamic code
    (r'\beval\s*\(',                                      'eval() — arbitrary code execution'),
    (r'\bFunction\s*\(',                                  'Function() — dynamic code execution'),

    # System
    (r"\brequire\s*\(\s*['\"]os['\"]\s*\)",               'require("os") — system info'),
    (r"\brequire\s*\(\s*['\"]vm['\"]\s*\)",               'require("vm") — VM sandbox escape'),
    (r"\brequire\s*\(\s*['\"]cluster['\"]\s*\)",          'require("cluster") — process forking'),
    (r'/etc/passwd',                                      '/etc/passwd — system file access'),
    (r'/proc/',                                           '/proc/ — process introspection'),
])


# ── C / C++ ───────────────────────────────────────────────────────────────────
_C_PATTERNS = _compile([
    # Process / shell
    (r'\bsystem\s*\(',                                    'system() — shell execution'),
    (r'\bpopen\s*\(',                                     'popen() — process piping'),
    (r'\bexecl[pe]?\s*\(',                                'exec family — process execution'),
    (r'\bexecv[pe]?\s*\(',                                'exec family — process execution'),
    (r'\bfork\s*\(',                                      'fork() — process forking'),

    # File system (allow stdin/stdout, block explicit file ops)
    (r'\bfopen\s*\(',                                     'fopen() — file access'),
    (r'\bfreopen\s*\(',                                   'freopen() — file redirection'),
    (r'\bremove\s*\(',                                    'remove() — file deletion'),
    (r'\brename\s*\(',                                    'rename() — file renaming'),
    (r'\bunlink\s*\(',                                    'unlink() — file deletion'),
    (r'\bmkdir\s*\(',                                     'mkdir() — directory creation'),
    (r'\brmdir\s*\(',                                     'rmdir() — directory deletion'),
    (r'\bopendir\s*\(',                                   'opendir() — directory listing'),

    # Network
    (r'#\s*include\s*<\s*sys/socket\.h\s*>',              'sys/socket.h — raw sockets'),
    (r'#\s*include\s*<\s*netinet/',                       'netinet — network headers'),
    (r'#\s*include\s*<\s*arpa/',                          'arpa — network headers'),
    (r'\bsocket\s*\(',                                    'socket() — network access'),
    (r'\bconnect\s*\(',                                   'connect() — network access'),
    (r'\bbind\s*\(',                                      'bind() — network listener'),

    # Dynamic loading
    (r'\bdlopen\s*\(',                                    'dlopen() — dynamic library loading'),
    (r'\bdlsym\s*\(',                                     'dlsym() — dynamic symbol resolution'),

    # Environment / system
    (r'\bgetenv\s*\(',                                    'getenv() — environment access'),
    (r'\bsetenv\s*\(',                                    'setenv() — environment manipulation'),
    (r'/etc/passwd',                                      '/etc/passwd — system file access'),
    (r'/proc/',                                           '/proc/ — process introspection'),
])


# ── Java ──────────────────────────────────────────────────────────────────────
_JAVA_PATTERNS = _compile([
    # Process / shell
    (r'\bRuntime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\b',  'Runtime.exec() — shell execution'),
    (r'\bProcessBuilder\b',                               'ProcessBuilder — process spawning'),

    # File system
    (r'\bnew\s+File\b',                                   'new File — file system access'),
    (r'\bFileInputStream\b',                              'FileInputStream — file reading'),
    (r'\bFileOutputStream\b',                             'FileOutputStream — file writing'),
    (r'\bFiles\s*\.\s*(read|write|delete|copy|move)\b',   'Files API — file operations'),
    (r'\bBufferedReader\b',                               'BufferedReader — file reading'),
    (r'\bFileReader\b',                                   'FileReader — file reading'),
    (r'\bFileWriter\b',                                   'FileWriter — file writing'),

    # Network
    (r'\bjava\s*\.\s*net\b',                              'java.net — network access'),
    (r'\bSocket\b',                                       'Socket — raw network access'),
    (r'\bServerSocket\b',                                 'ServerSocket — network listener'),
    (r'\bURL\b',                                          'URL — HTTP requests'),
    (r'\bHttpURLConnection\b',                            'HttpURLConnection — HTTP client'),
    (r'\bDatagramSocket\b',                               'DatagramSocket — UDP sockets'),

    # Reflection / dynamic code
    (r'\bjava\s*\.\s*lang\s*\.\s*reflect\b',              'reflection — dynamic code execution'),
    (r'\bClass\s*\.\s*forName\b',                         'Class.forName — dynamic class loading'),
    (r'\bClassLoader\b',                                  'ClassLoader — dynamic class loading'),

    # System
    (r'\bSystem\s*\.\s*getenv\b',                         'System.getenv — environment access'),
    (r'\bSystem\s*\.\s*getProperty\b',                    'System.getProperty — system property access'),
    (r'\bSystem\s*\.\s*exit\b',                           'System.exit — forced JVM exit'),
    (r'/etc/passwd',                                      '/etc/passwd — system file access'),
    (r'/proc/',                                           '/proc/ — process introspection'),
])


BLOCKLISTS = {
    "python":     _PYTHON_PATTERNS,
    "javascript": _JS_PATTERNS,
    "c":          _C_PATTERNS,
    "cpp":        _C_PATTERNS,
    "java":       _JAVA_PATTERNS,
}

def sanitize_code(lang: str, code: str) -> dict:
    """
    Scan submitted code for dangerous patterns.

    Returns:
        {
            "safe": True/False,
            "violations": ["reason1", "reason2", ...]
        }
    """
    patterns = BLOCKLISTS.get(lang, [])
    violations = []

    for regex, reason in patterns:
        if regex.search(code):
            violations.append(reason)

    return {
        "safe": len(violations) == 0,
        "violations": violations,
    }
