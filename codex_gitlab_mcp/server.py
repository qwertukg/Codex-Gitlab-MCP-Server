from fastapi import FastAPI, HTTPException, Request
from fastapi import Body

from .client import GitlabClient


class GitlabMCPServer:
    """MCP сервер для взаимодействия Codex с GitLab."""

    def __init__(self, client: GitlabClient | None = None) -> None:
        self.client = client or GitlabClient()
        self.app = FastAPI(title="Codex Gitlab MCP")
        self._register_routes()

    def _register_routes(self) -> None:
        @self.app.post("/webhook")
        async def webhook(request: Request):
            payload = await request.json()
            object_kind = payload.get("object_kind")
            if object_kind == "issue":
                await self.handle_issue_event(payload)
            return {"status": "ok"}

        @self.app.get("/mr/{iid}/diff")
        async def mr_diff(iid: int):
            return {"diff": self.client.get_diff(iid)}

        @self.app.post("/mr/{iid}/notes")
        async def mr_note(iid: int, body: str = Body(..., embed=True)):
            self.client.add_note(iid, body)
            return {"status": "created"}

        @self.app.get("/repository")
        async def repo(path: str = "", ref: str | None = None):
            return self.client.repository_tree(path=path, ref=ref)

    async def handle_issue_event(self, payload: dict) -> None:
        issue = payload.get("object_attributes", {})
        labels = issue.get("labels", []) or payload.get("labels", [])
        label_names = {l["title"] for l in labels if isinstance(l, dict)}
        if "todo-dev" in label_names:
            iid = issue.get("iid")
            title = issue.get("title", f"Issue {iid}")
            description = issue.get("description", "")
            branch_name = f"issue-{iid}"
            try:
                self.client.create_merge_request(branch_name, title, description)
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=400, detail=str(exc))
