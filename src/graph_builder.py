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


def build_dependency_graph(start_package, max_depth, filter_substring, config):
    """Строит граф зависимостей с помощью итеративного DFS (без рекурсии)."""
    graph = {}
    stack = [(start_package, 0)]

    is_test = config.get("test_mode", False)
    test_repo = load_test_repo(config.get("test_repo_path", "")) \
        if is_test else {}

    if is_test and not test_repo:
        return {}

    while stack:
        current_pkg, depth = stack.pop()

        if current_pkg in graph:
            continue

        if depth >= max_depth:
            continue

        if filter_substring and filter_substring in current_pkg:
            continue

        deps = (
            test_repo.get(current_pkg, [])
            if is_test
            else fetch_real_deps(current_pkg, config["repository_url"])
        )
        graph[current_pkg] = deps

        for dep in deps:
            if filter_substring and filter_substring in dep:
                continue
            if dep not in graph:
                stack.append((dep, depth + 1))

    return graph