import json
import os
from fetcher import (
    search_maven_package,
    build_pom_url,
    download_pom,
    parse_direct_dependencies,
)


def load_test_repo(path):
    """Загружает тестовый репозиторий из JSON-файла."""
    if not os.path.isfile(path):
        print(f"ошибка: файл тестового репозитория не найден: {path}")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ошибка: неверный формат JSON: {e}")
        return {}


def fetch_real_deps(package_name, repo_url):
    """Получает зависимости реального пакета из Maven."""
    group_id, version = search_maven_package(package_name)
    if not group_id or not version:
        return []

    pom_url = build_pom_url(group_id, package_name, version, repo_url)
    pom_content = download_pom(pom_url)

    if not pom_content:
        return []

    return parse_direct_dependencies(pom_content, self_artifact=package_name)


def should_skip_package(pkg, graph, depth, max_depth, filter_substring):
    """Проверяет, нужно ли пропустить пакет при обходе."""
    if pkg in graph:
        return True
    if depth >= max_depth:
        return True
    if filter_substring and filter_substring in pkg:
        return True
    return False


def get_package_deps(pkg, is_test, test_repo, repo_url):
    """Получает зависимости пакета (из теста или реального репозитория)."""
    if is_test:
        return test_repo.get(pkg, [])
    return fetch_real_deps(pkg, repo_url)


def add_deps_to_stack(deps, graph, depth, filter_substring, stack):
    """Добавляет валидные зависимости в стек обхода."""
    for dep in deps:
        if filter_substring and filter_substring in dep:
            continue
        if dep not in graph:
            stack.append((dep, depth + 1))


def build_dependency_graph(
    start_package, max_depth, filter_substring, config
):
    """Строит граф зависимостей с помощью итеративного DFS."""
    graph = {}
    stack = [(start_package, 0)]

    is_test = config.get("test_mode", False)
    test_repo = (
        load_test_repo(config.get("test_repo_path", ""))
        if is_test
        else {}
    )

    if is_test and not test_repo:
        return {}

    repo_url = config["repository_url"]

    while stack:
        current_pkg, depth = stack.pop()

        if should_skip_package(
            current_pkg, graph, depth, max_depth, filter_substring
        ):
            continue

        deps = get_package_deps(
            current_pkg, is_test, test_repo, repo_url
        )
        graph[current_pkg] = deps

        add_deps_to_stack(
            deps, graph, depth, filter_substring, stack
        )

    return graph