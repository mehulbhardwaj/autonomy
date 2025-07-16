from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Optional

import requests


class GraphQLClient:
    """Minimal GitHub GraphQL client."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.url = "https://api.github.com/graphql"

    def execute(self, query: str, variables: Optional[dict] = None) -> dict:
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": variables or {}},
            timeout=10,
        )
        if response.status_code != 200:
            raise ValueError(f"GraphQL error: {response.status_code} {response.text}")
        data = response.json()
        if data.get("errors"):
            raise ValueError(str(data["errors"]))
        return data.get("data", {})


class BoardManager:
    """Manage GitHub Projects v2 board."""

    REQUIRED_FIELDS = {
        "Priority": ("SINGLE_SELECT", ["P0", "P1", "P2", "P3"]),
        "Pinned": ("SINGLE_SELECT", ["Yes", "No"]),
        "Sprint": ("ITERATION", []),
        "Track": ("TEXT", []),
    }

    def __init__(
        self,
        github_token: str,
        owner: str,
        repo: str,
        cache_path: Optional[Path] = None,
    ) -> None:
        self.client = GraphQLClient(github_token)
        self.owner = owner
        self.repo = repo
        self.cache_path = cache_path or Path.home() / ".autonomy" / "field_cache.json"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def _load_cache(self) -> Dict[str, str]:
        if self.cache_path.exists():
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self, data: Dict[str, str]) -> None:
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    # ------------------------------------------------------------------
    def _find_or_create_project(self) -> str:
        query = """
        query RepoProjects($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            id
            projectsV2(first: 20) { nodes { id title } }
          }
        }
        """
        data = self.client.execute(query, {"owner": self.owner, "repo": self.repo})
        repo = data["repository"]
        repo_id = repo["id"]
        for node in repo.get("projectsV2", {}).get("nodes", []):
            if node.get("title") == "Autonomy Board":
                return node["id"]
        mutation = """
        mutation CreateProject($ownerId: ID!, $title: String!) {
          createProjectV2(input: {ownerId: $ownerId, title: $title}) {
            projectV2 { id }
          }
        }
        """
        resp = self.client.execute(
            mutation, {"ownerId": repo_id, "title": "Autonomy Board"}
        )
        return resp["createProjectV2"]["projectV2"]["id"]

    def _get_fields(self, project_id: str) -> Dict[str, str]:
        query = """
        query GetFields($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2FieldCommon { id name }
                }
              }
            }
          }
        }
        """
        data = self.client.execute(query, {"projectId": project_id})
        fields = {}
        nodes = data.get("node", {}).get("fields", {}).get("nodes", [])
        for node in nodes:
            name = node.get("name")
            if name:
                fields[name] = node.get("id")
        return fields

    def _create_field(self, project_id: str, name: str, data_type: str) -> str:
        mutation = """
        mutation CreateField($projectId: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!) {
          createProjectV2Field(input: {projectId: $projectId, name: $name, dataType: $dataType}) {
            projectV2Field { id }
          }
        }
        """
        data = self.client.execute(
            mutation,
            {"projectId": project_id, "name": name, "dataType": data_type},
        )
        print(f"Created field {name}")
        return data["createProjectV2Field"]["projectV2Field"]["id"]

    def _add_option(self, field_id: str, name: str) -> None:
        mutation = """
        mutation AddFieldOption($fieldId: ID!, $name: String!) {
          addProjectV2FieldOption(input: {fieldId: $fieldId, name: $name}) {
            projectV2SingleSelectFieldOption { id }
          }
        }
        """
        self.client.execute(mutation, {"fieldId": field_id, "name": name})
        print(f"Added option {name} to field {field_id}")

    def _get_field_options(self, field_id: str) -> set[str]:
        query = """
        query FieldOptions($fieldId: ID!) {
          node(id: $fieldId) {
            ... on ProjectV2SingleSelectField {
              options(first: 20) { nodes { name } }
            }
          }
        }
        """
        data = self.client.execute(query, {"fieldId": field_id})
        nodes = data.get("node", {}).get("options", {}).get("nodes", [])
        return {n.get("name") for n in nodes if n.get("name")}

    def _ensure_options(self, field_id: str, options: Iterable[str]) -> None:
        existing = self._get_field_options(field_id)
        for opt in options:
            if opt not in existing:
                self._add_option(field_id, opt)

    # ------------------------------------------------------------------
    def init_board(self) -> Dict[str, str]:
        """Ensure project and required fields exist. Returns field cache."""
        project_id = self._find_or_create_project()
        existing = self._get_fields(project_id)
        cache = self._load_cache()
        cache.update({k: v for k, v in existing.items() if k in self.REQUIRED_FIELDS})
        for name, (ftype, options) in self.REQUIRED_FIELDS.items():
            field_id = existing.get(name)
            if not field_id:
                field_id = self._create_field(project_id, name, ftype)
                cache[name] = field_id
            if options and ftype == "SINGLE_SELECT":
                self._ensure_options(field_id, options)
        self._save_cache(cache)
        return cache
