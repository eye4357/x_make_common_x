from collections.abc import Mapping, Sequence
from pathlib import Path

class RepoRecord:
    name: str
    full_name: str
    clone_url: str | None
    ssh_url: str | None
    fork: bool

    def __init__(
        self,
        name: str,
        full_name: str,
        clone_url: str | None,
        ssh_url: str | None,
        fork: bool,
    ) -> None: ...
    def matches(self, names: set[str] | None) -> bool: ...
    def resolved_clone_url(
        self,
        token: str | None,
        *,
        allow_token_clone: bool,
    ) -> str: ...

class XClsMakeGithubClonesX:
    ALLOW_TOKEN_CLONE_ENV: str
    USER_AGENT: str
    exit_code: int
    last_run_report_path: Path | None
    token: str | None

    def __init__(
        self,
        username: str | None = ...,
        *,
        target_dir: str | None = ...,
        names: Sequence[str] | None = ...,
        token: str | None = ...,
        ctx: object | None = ...,
        cloner: object | None = ...,
        report_base_dir: str | None = ...,
    ) -> None: ...
    def set_report_base_dir(self, base_dir: Path | str) -> None: ...
    def fetch_repos(
        self,
        username: str | None = ...,
        *,
        include_forks: bool | None = ...,
    ) -> list[RepoRecord]: ...
    def sync(self) -> int: ...
    def allow_token_clone(self) -> bool: ...

x_cls_make_github_clones_x: type[XClsMakeGithubClonesX]

def resolve_workspace_root(parameters: Mapping[str, object]) -> str: ...
def synchronize_workspace(
    payload: Mapping[str, object],
    *,
    ctx: object | None = ...,
) -> dict[str, object]: ...
def main_json(payload: Mapping[str, object]) -> dict[str, object]: ...
