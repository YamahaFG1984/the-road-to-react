#!/usr/bin/env python3
"""
把 docs-src/ 里的章节源文件生成成 docs/ 下可直接部署到 GitHub Pages 的静态 HTML。

源文件就是 HTML 片段，外加两个便利写法：

1. 代码围栏（不需要手动转义 < > &）：

       ```jsx src/App.jsx
       const App = () => <h1>Hello</h1>;
       ```

   第一行是 ```语言 [文件名/标题]；构建时会转义并做语法高亮。
   想在对照卡片里去掉外边框，照常写在 <div class="vs"> 里即可。

2. 行内代码：正文里的 `code` 会变成 <code>code</code>（内容自动转义）。
   <svg>、<script>、<style> 块内部不做这个替换。

用法：python3 tools/build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs-src'
OUT = ROOT / 'docs'

SITE_TITLE = 'React 19 入门教程'

CHAPTERS = [
    # n, 标题, 一句话描述, 所属部分（只在每部分第一章写）
    (1,  '你好，React',              '网页从服务器渲染走到单页应用，React 为什么会赢', '第一部分 · 起步'),
    (2,  '用 Vite 创建项目',          '环境准备、项目结构与 npm 脚本', None),
    (3,  '第一个 React 组件',          '组件就是一个返回 UI 的函数', '第二部分 · 组件与 JSX'),
    (4,  'JSX：在 JavaScript 里写界面', '花括号、className、htmlFor 以及 JSX 编译成什么', None),
    (5,  '渲染列表与 key',             'map() 把数组变成元素，key 让 React 认得每一项', None),
    (6,  '组件树、实例与 React DOM',    '拆分组件、声明与实例、createRoot 挂载', None),
    (7,  '组件的几种写法',             '函数声明、箭头函数与隐式返回', None),
    (8,  '事件处理函数',               '声明式地响应用户操作', '第三部分 · 交互与数据流'),
    (9,  'Props：父传子',             '用属性把数据往下传', None),
    (10, 'State 与 useState',          '让组件记住会变化的值', None),
    (11, '回调与状态提升',             '子组件怎么通知父组件，状态应该放在哪', None),
    (12, '受控组件',                   '让表单元素听 React 的', None),
    (13, 'Props 进阶技巧',             '解构、默认值、展开与剩余运算符', None),
    (14, '副作用与 useEffect',         '把 localStorage、网络请求放到渲染之外', '第四部分 · Hooks 与组件模式'),
    (15, '自定义 Hook',                '把状态逻辑抽出来复用', None),
    (16, 'Fragment、复用与组合',        '<>…</>、通用组件与 children', None),
    (17, '命令式 React 与 ref',        'useRef 操作 DOM，React 19 的 ref 新变化', None),
    (18, '内联处理函数：删除条目',      '把参数“夹带”进事件处理函数', None),
    (19, '异步数据与条件渲染',          '模拟请求、加载中与出错状态', '第五部分 · 异步数据与表单'),
    (20, 'useReducer 与“不可能状态”',  '把相关的状态收拢到一个 reducer', None),
    (21, '获取真实数据',               '接入 Hacker News API，从客户端搜索到服务端搜索', None),
    (22, 'useCallback 与显式获取',      '记忆化函数、依赖链与按钮触发请求', None),
    (23, '第三方库与 async/await',      'axios 与更易读的异步代码', None),
    (24, '表单与 Actions',             '从 onSubmit 到 React 19 的 form action', None),
    (25, 'React 学习路线图',           'Context、use()、服务端组件与下一步', None),
    (26, 'CSS 与 CSS Modules',         '全局样式、行内样式与作用域样式', '第六部分 · 样式'),
    (27, 'CSS-in-JS 与 SVG',           'styled-components、Tailwind 与图标', None),
    (28, '性能优化',                   'StrictMode、memo、useCallback、useMemo 与 React Compiler', '第七部分 · 维护'),
    (29, 'TypeScript + React',        '给组件、Hook 和 reducer 加上类型', None),
    (30, '测试入门：Vitest',            '测试金字塔、单元测试与组件测试', None),
    (31, '集成测试与快照测试',          'mock 网络请求，像用户一样测试整个应用', None),
    (32, '项目结构',                   '从单文件到按功能组织的目录', None),
    (33, '排序与反向排序',             '表头按钮、排序字典与 lodash', '第八部分 · 实战进阶'),
    (34, '记住最近的搜索',             '用 URL 数组记录搜索历史', None),
    (35, '分页加载更多',               '无限分页与“加载更多”按钮', None),
    (36, '路由：React Router',         '多页面、URL 参数、搜索参数与文章详情页', '第九部分 · 进阶专题'),
    (37, 'Context 实战',               '主题切换与收藏夹：何时用 Context，何时不用', None),
    (38, '错误边界与 Suspense',         '优雅地处理加载中与渲染出错', None),
    (39, '防抖与并发渲染',             '防抖搜索、useTransition 与 useDeferredValue', None),
    (40, 'TanStack Query',            '用服务端状态库重写数据请求与无限加载', None),
    (41, '乐观更新与表单校验',          'useOptimistic、React Hook Form 与 Zod', None),
    (42, '调试与 React DevTools',       '定位 bug 与“为什么又重新渲染了”', None),
    (43, '可访问性',                   '语义化、键盘、焦点与读屏软件', None),
    (44, 'React 生态地图与选型方法',     '面对上百个库，怎么挑、怎么判断', '第十部分 · 生态与选型'),
    (45, '状态管理库选型',             'Context、Zustand、Redux Toolkit、Jotai 对比', None),
    (46, '数据请求库选型',             'TanStack Query、SWR、RTK Query、Apollo、tRPC', None),
    (47, 'UI 组件库与样式选型',          'shadcn/ui、Ant Design、MUI、Mantine 等', None),
    (48, '常用工具库',                 '表单、校验、日期、国际化、动画、图表、工具函数', None),
    (49, '路由与框架选型',             'React Router、TanStack Router、Next.js、Astro', None),
    (50, '组合实战：搭一套技术栈',       '把常用库组合进一个项目', None),
    (51, 'Next.js 入门',               '服务端组件、服务端函数与全栈 React', '第十一部分 · 全栈与上线'),
    (52, '构建与部署',                 'npm run build、Firebase 与 GitHub Pages', None),
    (53, '下一步去哪里',               '全书速查、新旧对照与继续学习的方向', None),
]

KW = ('const|let|var|function|return|if|else|await|async|import|from|export|default|new|class|'
      'extends|implements|for|while|of|in|do|try|catch|finally|throw|switch|case|break|continue|'
      'type|interface|enum|as|satisfies|typeof|instanceof|delete|void|yield|public|private|readonly|'
      'null|undefined|true|false|this|super|static|declare|namespace|keyof').split('|')

RE_JS = re.compile(
    r'(\{/\*[\s\S]*?\*/\}|/\*[\s\S]*?\*/|//[^\n]*)'                        # 1 注释
    r'|(`(?:\\[\s\S]|[^\\`])*`|\'(?:\\.|[^\\\'\n])*\'|"(?:\\.|[^\\"\n])*")'  # 2 字符串
    r'|(</?(?=[A-Za-z>])[A-Za-z][\w.]*|</?>|/>)'                           # 3 JSX 标签
    r'|\b(' + '|'.join(KW) + r')\b'                                        # 4 关键字
    r'|\b([A-Z][A-Za-z0-9_]*)\b'                                           # 5 类型/组件
    r'|\b(\d+(?:\.\d+)?)\b'                                                # 6 数字
    r'|\b([a-zA-Z_$][\w$]*)(?=\()'                                         # 7 函数调用
)
JS_CLASSES = ['tk-cm', 'tk-st', 'tk-tg', 'tk-kw', 'tk-tp', 'tk-nm', 'tk-fn']

RE_SH = re.compile(
    r'(#[^\n]*)|(\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*")'
    r'|(?<![\w-])(npm|npx|pnpm|yarn|node|git|cd|mkdir|touch|mv|curl|firebase|code|ls|pwd|rm|cp)(?![\w-])'
)
SH_CLASSES = ['tk-cm', 'tk-st', 'tk-kw']

RE_CSS = re.compile(
    r'(/\*[\s\S]*?\*/)|(\'[^\']*\'|"[^"]*")|(#[0-9a-fA-F]{3,8}\b)'
    r'|([\w-]+)(?=\s*:[^:{]*;)|(\b\d+(?:\.\d+)?(?:px|em|rem|vw|vh|%|s|ms)?\b)'
)
CSS_CLASSES = ['tk-cm', 'tk-st', 'tk-nm', 'tk-pr', 'tk-nm']

RE_JSON = re.compile(r'("(?:\\.|[^\\"])*")(?=\s*:)|("(?:\\.|[^\\"])*")|\b(true|false|null)\b|(\b\d+\b)')
JSON_CLASSES = ['tk-pr', 'tk-st', 'tk-kw', 'tk-nm']


def paint(src, rx, classes):
    out, last = [], 0
    for m in rx.finditer(src):
        out.append(html.escape(src[last:m.start()], quote=False))
        for g, cls in enumerate(classes, start=1):
            if m.group(g) is not None:
                out.append('<span class="%s">%s</span>' % (cls, html.escape(m.group(g), quote=False)))
                break
        last = m.end()
    out.append(html.escape(src[last:], quote=False))
    return ''.join(out)


def highlight(code, lang):
    if lang in ('js', 'jsx', 'ts', 'tsx', 'javascript', 'typescript'):
        return paint(code, RE_JS, JS_CLASSES)
    if lang in ('bash', 'sh', 'shell'):
        return paint(code, RE_SH, SH_CLASSES)
    if lang in ('css', 'scss'):
        return paint(code, RE_CSS, CSS_CLASSES)
    if lang == 'json':
        return paint(code, RE_JSON, JSON_CLASSES)
    return html.escape(code, quote=False)


LANG_LABEL = {'jsx': 'JSX', 'js': 'JavaScript', 'ts': 'TypeScript', 'tsx': 'TSX', 'bash': '命令行',
              'sh': '命令行', 'css': 'CSS', 'json': 'JSON', 'html': 'HTML', 'text': '输出',
              'console': '控制台输出', 'tree': '目录结构'}

FENCE = re.compile(r'^([ \t]*)```(\w+)?[ \t]*(.*?)[ \t]*\n(.*?)^\1```[ \t]*$', re.M | re.S)


def render_fence(m):
    indent, lang, title, body = m.group(1), (m.group(2) or 'text'), m.group(3), m.group(4)
    lines = body.split('\n')
    if indent:
        lines = [ln[len(indent):] if ln.startswith(indent) else ln for ln in lines]
    code = '\n'.join(lines).rstrip('\n')
    label = title or LANG_LABEL.get(lang, lang)
    extra = ' console' if lang == 'console' else ''
    return ('<div class="code%s" data-lang="%s"><div class="bar"><span class="tag">%s</span></div>'
            '<pre>%s</pre></div>') % (extra, lang, html.escape(label), highlight(code, lang))


PROTECT = re.compile(r'(<svg[\s\S]*?</svg>|<script[\s\S]*?</script>|<style[\s\S]*?</style>|'
                     r'<div class="code[\s\S]*?</pre></div>)')
INLINE = re.compile(r'`([^`\n]+)`')


def inline_code(text):
    parts = PROTECT.split(text)
    for i in range(0, len(parts), 2):
        parts[i] = INLINE.sub(lambda m: '<code>%s</code>' % html.escape(m.group(1), quote=False), parts[i])
    return ''.join(parts)


def transform(src):
    return inline_code(FENCE.sub(render_fence, src))


HEAD = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚛</text></svg>">
<script>try{{var t=localStorage.getItem('r2r-doc-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-chapter="{n}">
<div id="app">
<aside id="sidebar"></aside>
<main>
'''

FOOT = '''
</main>
</div>
<script src="assets/chapters.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
'''


def build():
    chapters_js = []
    part = None
    for n, t, d, p in CHAPTERS:
        item = {'n': n, 't': t, 'd': d}
        if p:
            item['part'] = p
        chapters_js.append(item)
    (OUT / 'assets').mkdir(parents=True, exist_ok=True)
    (OUT / 'assets' / 'chapters.js').write_text(
        '// 由 tools/build.py 生成，请勿手改\nwindow.CHAPTERS = ' +
        json.dumps(chapters_js, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')

    built, missing = 0, []
    idx = SRC / 'index.html'
    if idx.exists():
        body = transform(idx.read_text(encoding='utf-8'))
        page = HEAD.format(title=SITE_TITLE + ' · The Road to React 学习版',
                           desc='面向初学者的 React 19 中文教程', n=0) + body + FOOT
        (OUT / 'index.html').write_text(page, encoding='utf-8')
        built += 1

    for n, t, d, p in CHAPTERS:
        cur_part = p or part
        part = cur_part
        f = SRC / ('ch%02d.html' % n)
        if not f.exists():
            missing.append(n)
            continue
        body = transform(f.read_text(encoding='utf-8'))
        top = ('<span class="chapter-eyebrow">第 %d 章 · %s</span>\n<h1>%s</h1>\n'
               % (n, html.escape(cur_part.split('·')[-1].strip()), html.escape(t)))
        page = (HEAD.format(title='第 %d 章 · %s — %s' % (n, html.escape(t), SITE_TITLE),
                            desc=html.escape(d), n=n)
                + top + body + '\n<div id="pager"></div>' + FOOT)
        (OUT / ('ch%02d.html' % n)).write_text(page, encoding='utf-8')
        built += 1
    print('built %d pages' % built + (' (missing: %s)' % missing if missing else ''))


if __name__ == '__main__':
    (OUT / '.nojekyll').touch()
    build()
