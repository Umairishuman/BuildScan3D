"""server/runpod_client.py: the RunPod API client and the ssh/scp helpers, with the network and subprocesses faked."""
import types

import pytest

import server.runpod_client as rc


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status = payload, status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")


@pytest.fixture
def post(monkeypatch):
    """Replace requests.post; the test sets .reply to what RunPod should answer and reads .calls afterwards."""
    state = types.SimpleNamespace(reply=FakeResponse({"data": {}}), calls=[])

    def fake_post(url, json=None, params=None, headers=None):
        state.calls.append(types.SimpleNamespace(url=url, json=json, params=params, headers=headers))
        return state.reply

    monkeypatch.setattr(rc.requests, "post", fake_post)
    return state


# ------------------------------------------------------------------ API client
def test_query_sends_the_key_as_a_parameter_and_returns_the_data(post):
    post.reply = FakeResponse({"data": {"hello": "world"}})
    out = rc.RunPodClient("my-key")._query("query { x }", {"a": 1})
    assert out == {"hello": "world"}
    call = post.calls[0]
    assert call.url == rc.RUNPOD_API and call.params == {"api_key": "my-key"}
    assert call.json == {"query": "query { x }", "variables": {"a": 1}}


def test_query_raises_on_graphql_errors(post):
    post.reply = FakeResponse({"errors": [{"message": "bad key"}]})
    with pytest.raises(RuntimeError, match="RunPod API error"):
        rc.RunPodClient("k")._query("q")


def test_query_raises_on_http_errors(post):
    post.reply = FakeResponse({}, status=401)
    with pytest.raises(RuntimeError, match="401"):
        rc.RunPodClient("k")._query("q")


def test_create_pod_requests_the_gpu_and_parses_the_answer(post):
    post.reply = FakeResponse({"data": {"podFindAndDeployOnDemand": {
        "id": "pod42", "desiredStatus": "RUNNING", "machine": {"gpuDisplayName": "RTX 3090"}}}})
    info = rc.RunPodClient("k").create_pod(gpu_type="NVIDIA RTX 3090", disk_gb=80)
    assert (info.pod_id, info.status, info.gpu_type) == ("pod42", "RUNNING", "RTX 3090")
    sent = post.calls[0].json["variables"]["input"]
    assert sent["gpuTypeId"] == "NVIDIA RTX 3090" and sent["containerDiskInGb"] == 80 and sent["startSsh"] is True


def test_get_pod_finds_the_ssh_port(post):
    post.reply = FakeResponse({"data": {"pod": {
        "id": "p1", "desiredStatus": "RUNNING", "machine": {"gpuDisplayName": "RTX 3090"},
        "runtime": {"ports": [{"privatePort": 8888, "ip": "9.9.9.9", "publicPort": 1},
                              {"privatePort": 22, "ip": "1.2.3.4", "publicPort": 40022}]}}}})
    info = rc.RunPodClient("k").get_pod("p1")
    assert (info.ssh_host, info.ssh_port) == ("1.2.3.4", 40022)


def test_get_pod_without_runtime_has_no_ssh_yet(post):
    post.reply = FakeResponse({"data": {"pod": {"id": "p1", "desiredStatus": "RUNNING", "runtime": None}}})
    info = rc.RunPodClient("k").get_pod("p1")
    assert info.ssh_host is None and info.ssh_port is None


def test_get_pod_for_an_unknown_pod_raises(post):
    post.reply = FakeResponse({"data": {"pod": None}})
    with pytest.raises(RuntimeError, match="not found"):
        rc.RunPodClient("k").get_pod("ghost")


def test_wait_for_ready_returns_once_ssh_appears(monkeypatch):
    monkeypatch.setattr(rc.time, "sleep", lambda s: None)
    answers = iter([rc.PodInfo("p", "RUNNING"), rc.PodInfo("p", "RUNNING"), rc.PodInfo("p", "RUNNING", "h", 22)])
    client = rc.RunPodClient("k")
    monkeypatch.setattr(client, "get_pod", lambda pod_id: next(answers))
    info = client.wait_for_ready("p", timeout_sec=60)
    assert (info.ssh_host, info.ssh_port) == ("h", 22)


def test_wait_for_ready_times_out(monkeypatch):
    monkeypatch.setattr(rc.time, "sleep", lambda s: None)
    client = rc.RunPodClient("k")
    monkeypatch.setattr(client, "get_pod", lambda pod_id: rc.PodInfo("p", "RUNNING"))
    with pytest.raises(TimeoutError, match="not ready"):
        client.wait_for_ready("p", timeout_sec=0)


def test_terminate_pod_sends_the_pod_id(post):
    rc.RunPodClient("k").terminate_pod("pod7")
    assert post.calls[0].json["variables"] == {"input": {"podId": "pod7"}}
    assert "podTerminate" in post.calls[0].json["query"]


# ------------------------------------------------------------------ ssh / scp helpers
@pytest.fixture
def run(monkeypatch):
    state = types.SimpleNamespace(calls=[], result=types.SimpleNamespace(returncode=0, stderr="", stdout="ok"))

    def fake_run(cmd, **kw):
        state.calls.append(cmd)
        return state.result

    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    return state


def test_ssh_cmd_builds_the_expected_command(run):
    rc.ssh_cmd("1.2.3.4", 40022, "nvidia-smi")
    cmd = run.calls[0]
    assert cmd[0] == "ssh" and cmd[-1] == "nvidia-smi"
    assert "root@1.2.3.4" in cmd and cmd[cmd.index("-p") + 1] == "40022"
    assert "StrictHostKeyChecking=no" in cmd


def test_scp_upload_uses_capital_p_for_the_port_and_recursive_copy(run):
    rc.scp_upload("1.2.3.4", 40022, "/local/scan", "/workspace/")
    cmd = run.calls[0]
    assert cmd[0] == "scp" and cmd[cmd.index("-P") + 1] == "40022" and "-r" in cmd
    assert cmd[-2:] == ["/local/scan", "root@1.2.3.4:/workspace/"]


def test_scp_download_copies_from_the_pod(run):
    rc.scp_download("1.2.3.4", 22, "/workspace/out.ply", "out.ply")
    assert run.calls[0][-2:] == ["root@1.2.3.4:/workspace/out.ply", "out.ply"]


def test_scp_failures_raise_with_the_error_text(run):
    run.result = types.SimpleNamespace(returncode=1, stderr="Connection refused", stdout="")
    with pytest.raises(RuntimeError, match="Connection refused"):
        rc.scp_upload("h", 22, "a", "b")
    with pytest.raises(RuntimeError, match="Connection refused"):
        rc.scp_download("h", 22, "a", "b")
