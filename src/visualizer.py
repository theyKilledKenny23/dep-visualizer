import os
import subprocess


DOT_HEADER = "digraph dependencies {\n"
DOT_FOOTER = "}\n"
DOT_NODE_ATTR = '    node [shape=box, style=filled, fillcolor=lightblue];\n'


def _escape_label(name):
    """Экранирует специальные символы для DOT-разметки."""
    return name.replace('"', '\\"').replace("<", "\\<").replace(">", "\\>")


def _format_node(pkg, is_root=False):
    """Формирует строку описания узла графа."""
    label = _escape_label(pkg)
    if is_root:
        return f'    "{label}" [fillcolor=gold];\n'
    return f'    "{label}";\n'


def _format_edge(src, dst):
    """Формирует строку описания ребра графа."""
    src_label = _escape_label(src)
    dst_label = _escape_label(dst)
    return f'    "{src_label}" -> "{dst_label}";\n'


def generate_dot(graph, root_package):
    """Генерирует текстовое представление графа в формате DOT."""
    lines = [DOT_HEADER, DOT_NODE_ATTR]

    for pkg in graph:
        is_root = pkg == root_package
        lines.append(_format_node(pkg, is_root))

    for pkg, deps in graph.items():
        for dep in deps:
            if dep in graph:
                lines.append(_format_edge(pkg, dep))

    lines.append(DOT_FOOTER)
    return "".join(lines)


def save_dot_file(dot_content, output_path):
    """Сохраняет DOT-разметку в текстовый файл."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dot_content)
        print(f"DOT-файл сохранён: {output_path}")
        return True
    except OSError as e:
        print(f"ошибка записи DOT-файла: {e}")
        return False


def render_png(dot_path, png_path):
    """Рендерит PNG из DOT-файла через утилиту dot (Graphviz)."""
    if not os.path.isfile(dot_path):
        print(f"ошибка: DOT-файл не найден: {dot_path}")
        return False

    try:
        subprocess.run(
            ["dot", "-Tpng", dot_path, "-o", png_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"PNG-изображение сохранено: {png_path}")
        return True
    except FileNotFoundError:
        print(
            "ошибка: утилита 'dot' не найдена. "
            "Установите Graphviz или используйте только DOT-файл."
        )
        return False
    except subprocess.CalledProcessError as e:
        print(f"ошибка рендеринга PNG: {e.stderr}")
        return False