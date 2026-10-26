import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

SEARCH_API_URL = "https://search.maven.org/solrsearch/select"
MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}
USER_AGENT = "DepVisualizer/1.0"


def search_maven_package(package_name):
    """Ищет пакет в Maven Central и возвращает (groupId, version)."""
    query = f"?q=a:{package_name}&rows=1&wt=json"
    url = SEARCH_API_URL + query
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            return None, None
        return docs[0].get("g"), docs[0].get("latestVersion")
    except urllib.error.URLError as e:
        print(f"ошибка сети при поиске пакета: {e}")
        return None, None


def build_pom_url(group_id, artifact_id, version, repo_url):
    """Строит URL к POM-файлу на основе groupId."""
    group_path = group_id.replace(".", "/")
    base = repo_url.rstrip("/")
    return (f"{base}/{group_path}/{artifact_id}/{version}/{artifact_id}"
            f"-{version}.pom")


def download_pom(url):
    """Скачивает POM-файл по URL и возвращает его содержимое."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"ошибка скачивания POM: {e}")
        return None


def parse_direct_dependencies(pom_content):
    """Парсит XML POM и извлекает список прямых зависимостей."""
    try:
        root = ET.fromstring(pom_content)
    except ET.ParseError as e:
        print(f"ошибка парсинга XML: {e}")
        return []

    dependencies = []
    deps_nodes = root.findall(
        ".//m:dependencies/m:dependency", MAVEN_NS
    )
    if not deps_nodes:
        deps_nodes = root.findall(".//dependencies/dependency")

    for dep in deps_nodes:
        group = (
            dep.findtext("m:groupId", namespaces=MAVEN_NS)
            or dep.findtext("groupId")
        )
        artifact = (
            dep.findtext("m:artifactId", namespaces=MAVEN_NS)
            or dep.findtext("artifactId")
        )
        scope = (
            dep.findtext("m:scope", namespaces=MAVEN_NS)
            or dep.findtext("scope")
            or "compile"
        )

        if scope in ("test", "provided", "system"):
            continue

        if group and artifact:
            dependencies.append(f"{group}:{artifact}")

    return dependencies