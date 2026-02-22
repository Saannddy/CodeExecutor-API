import re

def _compile(patterns):
    return [(re.compile(p, re.IGNORECASE | re.MULTILINE), reason) for p, reason in patterns]

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
    # System / environment
    (r'\bos\s*\.\s*(environ|getenv)\b',                  'os.environ — environment access'),
    (r'/etc/passwd|/proc/',                               'system path access'),
])

_JS_PATTERNS = _compile([
    # Process / shell
    (r'\bchild_process\b',                                'child_process — shell execution'),
    (r'\bexecSync|spawnSync\b',                           'process spawning'),
    (r'\bprocess\.(exit|kill)\b',                         'process termination'),

    # File system
    (r"\brequire\s*\(\s*['\"]fs['\"]\s*\)",               'fs — file system access'),
    (r"\brequire\s*\(\s*['\"]path['\"]\s*\)",             'path — file system path manipulation'),
    (r"\brequire\s*\(\s*['\"]os['\"]\s*\)",               'os — system information'),
    (r'\bprocess\.cwd\(\)',                               'process.cwd() — path access'),

    # Network
    (r"\brequire\s*\(\s*['\"](net|http|https|dgram)['\"]\s*\)", 'network module access'),
    (r'\bfetch\s*\(',                                     'fetch() — network request'),

    # Dynamic code
    (r'\beval\s*\(',                                      'eval() — arbitrary code execution'),
    (r'\bFunction\s*\(',                                  'Function() — dynamic code execution'),
    (r"\brequire\s*\(\s*['\"](vm|cluster|worker_threads)['\"]\s*\)", 'low-level execution modules'),
    (r'\bprocess\.env\b',                                 'process.env — environment access'),
])

_C_PATTERNS = _compile([
    # Process / shell
    (r'\bsystem\s*\(',                                    'system() — shell execution'),
    (r'\bpopen\s*\(',                                     'popen() — pipe stream execution'),
    (r'\bexec[lvp][e]?\s*\(',                             'exec family — process execution'),
    (r'\bfork\s*\(',                                      'fork() — process spawning'),

    # File system
    (r'\bfopen\s*\(',                                     'fopen() — file access'),
    (r'\bfreopen\s*\(',                                   'freopen() — stream redirection'),
    (r'\bremove\s*\(',                                    'remove() — file deletion'),
    (r'\brmdir\s*\(',                                     'rmdir() — directory removal'),
    (r'\bunlink\s*\(',                                    'unlink() — file removal'),

    # Network
    (r'\bsocket\s*\(',                                    'socket() — network socket'),
    (r'\bconnect\s*\(',                                   'connect() — network connection'),
    (r'\bbind\s*\(',                                      'bind() — socket binding'),

    # System access
    (r'\bdlopen\s*\(',                                    'dlopen() — dynamic library loading'),
    (r'\bgetenv\s*\(',                                    'getenv() — environment access'),
    (r'\bsetenv\s*\(',                                    'setenv() — environment modification'),
    (r'/etc/passwd|/proc/',                               'system path access'),
])

_JAVA_PATTERNS = _compile([
    # Process / shell
    (r'\bRuntime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\b', 'Runtime.exec() — shell execution'),
    (r'\bProcessBuilder\b',                               'ProcessBuilder — process spawning'),

    # File system
    (r'\bnew\s+File\s*\(',                                'new File() — file system access'),
    (r'\bnew\s+File(Input|Output)Stream\s*\(',            'file stream access'),
    (r'\bnew\s+File(Reader|Writer)\s*\(',                 'file reader/writer access'),

    # Network
    (r'\bjava\.net\b',                                    'java.net — network package access'),
    (r'\bSocket\b',                                       'Socket — network connection'),
    (r'\bServerSocket\b',                                 'ServerSocket — network listening'),
    (r'\bURL\b',                                          'URL — network resource access'),

    # Dynamic code
    (r'\bjava\.lang\.reflect\b',                          'reflection — internal access'),
    (r'\bClass\.forName\b',                               'Class.forName — dynamic loading'),
    (r'\bSystem\.(exit|getenv)\b',                        'System manipulation — env/exit'),
    (r'/etc/passwd|/proc/',                               'system path access'),
])

DETECTORS = {
    "python": _PYTHON_PATTERNS,
    "javascript": _JS_PATTERNS,
    "c": _C_PATTERNS,
    "cpp": _C_PATTERNS,
    "java": _JAVA_PATTERNS,
}

def detect_violations(lang: str, code: str) -> dict:
    violations = []
    for regex, reason in DETECTORS.get(lang, []):
        if regex.search(code):
            if "Security policy violation prohibited code pattern detected." not in violations:
                violations.append("Security policy violation prohibited code pattern detected.")
                
    return {
        "safe": len(violations) == 0,
        "violations": violations
    }
