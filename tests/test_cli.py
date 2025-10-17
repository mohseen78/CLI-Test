import os
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent.parent
PY = sys.executable


def run_cli(args, env=None):
    cmd = [PY, str(HERE / "notes_cli.py")] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result


def test_list_all(tmp_path, monkeypatch):
    data = [
        {"text": "a", "label": "work", "created": "2025-01-01T00:00:00"},
        {"text": "b", "label": "personal", "created": "2025-01-02T00:00:00"},
    ]
    data_file = tmp_path / "notes.json"
    data_file.write_text(json.dumps(data))

    env = os.environ.copy()
    env["NOTES_DATA_FILE"] = str(data_file)

    r = run_cli(["list"], env=env)
    assert r.returncode == 0
    out = r.stdout.strip().splitlines()
    assert any("[work] a" in line for line in out)
    assert any("[personal] b" in line for line in out)


def test_list_label_filter(tmp_path):
    data = [
        {"text": "a", "label": "work", "created": "2025-01-01T00:00:00"},
        {"text": "b", "label": "personal", "created": "2025-01-02T00:00:00"},
    ]
    data_file = tmp_path / "notes.json"
    data_file.write_text(json.dumps(data))

    env = os.environ.copy()
    env["NOTES_DATA_FILE"] = str(data_file)

    r = run_cli(["list", "--label", "work"], env=env)
    assert r.returncode == 0
    out = r.stdout.strip().splitlines()
    assert any("[work] a" in line for line in out)
    assert all("[personal]" not in line for line in out)


def test_add_note_creates_file(tmp_path):
    data_file = tmp_path / "notes.json"
    env = os.environ.copy()
    env["NOTES_DATA_FILE"] = str(data_file)

    r = run_cli(["add", "Test note", "work"], env=env)
    assert r.returncode == 0
    assert data_file.exists()
    notes = json.loads(data_file.read_text())
    assert any(
        n["text"] == "Test note" and n["label"] == "work" for n in notes
    )
