import os
from typing import List

import gitlab


class GitlabClient:
    """Клиент GitLab, инкапсулирующий операции с API."""

    def __init__(self, url: str | None = None, token: str | None = None, project_id: int | None = None) -> None:
        self.url = url or os.environ.get("GITLAB_URL")
        self.token = token or os.environ.get("GITLAB_TOKEN")
        self.project_id = project_id or int(os.environ.get("GITLAB_PROJECT_ID", "0"))
        self._gl = gitlab.Gitlab(self.url, private_token=self.token)
        self._project = self._gl.projects.get(self.project_id)

    # -- Issues --
    def get_issue(self, issue_id: int):
        return self._project.issues.get(issue_id)

    # -- Merge Requests --
    def create_merge_request(self, source_branch: str, title: str, description: str) -> gitlab.v4.objects.ProjectMergeRequest:
        """Создаёт MR из указанной ветки в default_branch."""
        return self._project.mergerequests.create(
            {
                "source_branch": source_branch,
                "target_branch": self._project.default_branch,
                "title": title,
                "description": description,
            }
        )

    def add_note(self, mr_iid: int, body: str):
        mr = self._project.mergerequests.get(mr_iid)
        mr.notes.create({"body": body})

    def get_diff(self, mr_iid: int) -> str:
        mr = self._project.mergerequests.get(mr_iid)
        return mr.diffs.list()[0].diff if mr.diffs.list() else ""

    def repository_tree(self, path: str = "", ref: str | None = None) -> List[dict]:
        return self._project.repository_tree(path=path, ref=ref)
