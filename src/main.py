import json
import os
import sys
import argparse


CONFIG_FILE = "config.json"
REQUIRED_KEYS = [
    "package_name",
    "repository_url",
    "test_mode",
    "test_repo_path",
    "output_image",
    "max_depth",
    "filter_substring",
]

def parse_cli_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей Maven"
    )
    parser.add_argument(
        "-p", "--package",
        help="Имя пакета для анализа (переопределяет config.json)"
    )
    parser.add_argument(
        "-d", "--depth",
        type=int,
        help="Максимальная глубина анализа (переопределяет config.json)"
    )
    parser.add_argument(
        "-f", "--filter",
        help="Подстрока для фильтрации пакетов"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Включить режим тестирования"
    )
    parser.add_argument(
        "--test-repo",
        help="Путь к тестовому репозиторию"
    )
    parser.add_argument(
        "-c", "--config",
        default=CONFIG_FILE,
        help=f"Путь к файлу конфигурации (по умолчанию: {CONFIG_FILE})"
    )
    return parser.parse_args()


def merge_config(cli_args, file_config):
    """Объединяет конфиг из файла с CLI-аргументами.
    CLI имеет приоритет над файлом.
    """
    merged = dict(file_config)

    if cli_args.package:
        merged["package_name"] = cli_args.package
    if cli_args.depth is not None:
        merged["max_depth"] = cli_args.depth
    if cli_args.filter is not None:
        merged["filter_substring"] = cli_args.filter
    if cli_args.test_mode:
        merged["test_mode"] = True
    if cli_args.test_repo:
        merged["test_repo_path"] = cli_args.test_repo
        merged["test_mode"] = True

    return merged


def load_config(path):
    """Загружает конфигурацию из JSON-файла."""
    if not os.path.isfile(path):
        print(f"ошибка: файл конфигурации не найден: {path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ошибка: неверный формат JSON: {e}")
        sys.exit(1)

    return config


def validate_config(config):
    """Проверяет наличие всех обязательных параметров."""
    for key in REQUIRED_KEYS:
        if key not in config:
            print(f"ошибка: отсутствует параметр: {key}")
            sys.exit(1)


def validate_package_name(name):
    """Проверяет имя пакета."""
    if not isinstance(name, str) or not name.strip():
        print("ошибка: package_name должен быть непустой строкой")
        sys.exit(1)


def validate_repository_url(url, test_mode):
    """Проверяет URL репозитория."""
    if not isinstance(url, str) or not url.strip():
        print("ошибка: repository_url должен быть непустой строкой")
        sys.exit(1)

    if not test_mode and not url.startswith("http"):
        print("ошибка: repository_url должен начинаться с http")
        sys.exit(1)


def validate_test_mode(test_mode):
    """Проверяет режим тестирования."""
    if not isinstance(test_mode, bool):
        print("ошибка: test_mode должен быть true или false")
        sys.exit(1)


def validate_test_repo_path(path, test_mode):
    """Проверяет путь к тестовому репозиторию."""
    if test_mode:
        if not isinstance(path, str) or not path.strip():
            print(
                "ошибка: test_repo_path должен быть "
                "указан при test_mode=true"
            )
            sys.exit(1)
        if not os.path.isfile(path):
            print(f"ошибка: тестовый файл не найден: {path}")
            sys.exit(1)


def validate_output_image(image):
    """Проверяет имя выходного файла."""
    if not isinstance(image, str) or not image.strip():
        print("ошибка: output_image должен быть непустой строкой")
        sys.exit(1)


def validate_max_depth(depth):
    """Проверяет максимальную глубину."""
    if not isinstance(depth, int) or depth < 1:
        print("ошибка: max_depth должен быть целым числом >= 1")
        sys.exit(1)


def validate_filter_substring(substring):
    """Проверяет подстроку фильтрации."""
    if substring is None:
        print("ошибка: filter_substring не должен быть None")
        sys.exit(1)


def print_config(config):
    """Выводит все параметры конфигурации."""
    print("=== Параметры конфигурации ===")
    print(f"package_name: {config['package_name']}")
    print(f"repository_url: {config['repository_url']}")
    print(f"test_mode: {config['test_mode']}")
    print(f"test_repo_path: {config['test_repo_path']}")
    print(f"output_image: {config['output_image']}")
    print(f"max_depth: {config['max_depth']}")
    print(f"filter_substring: {config['filter_substring']}")
    print("================================")

def fetch_dependencies(config):
    """Получает и выводит прямые зависимости пакета (Этап 2)."""
    from fetcher import (
        search_maven_package,
        build_pom_url,
        download_pom,
        parse_direct_dependencies,
    )

    print("\n=== Сбор данных о зависимостях ===")
    artifact_id = config["package_name"]
    print(f"Поиск пакета: {artifact_id}...")

    group_id, version = search_maven_package(artifact_id)

    if not group_id or not version:
        print(f"ошибка: пакет '{artifact_id}' не найден")
        sys.exit(1)

    print(f"Найдено: {group_id}:{artifact_id} (версия {version})")

    pom_url = build_pom_url(
        group_id, artifact_id, version, config["repository_url"]
    )
    print(f"Загрузка POM: {pom_url}")

    pom_content = download_pom(pom_url)
    if not pom_content:
        print("ошибка: не удалось загрузить POM-файл")
        sys.exit(1)

    dependencies = parse_direct_dependencies(pom_content)
    print(f"\nПрямые зависимости ({len(dependencies)}):")
    for dep in dependencies:
        print(f"  - {dep}")
    print("================================\n")

cli_args = parse_cli_args()
config = load_config(cli_args.config)
validate_config(config)

config = merge_config(cli_args, config)

validate_package_name(config["package_name"])
validate_repository_url(
    config["repository_url"], config["test_mode"]
)
validate_test_mode(config["test_mode"])
validate_test_repo_path(
    config["test_repo_path"], config["test_mode"]
)
validate_output_image(config["output_image"])
validate_max_depth(config["max_depth"])
validate_filter_substring(config["filter_substring"])

print_config(config)

fetch_dependencies(config)