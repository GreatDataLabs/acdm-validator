import json
from pathlib import Path

from acdm_validator.cli.main import main

ROOT = Path(__file__).parents[1]


def test_cli_success(capsys):
    code = main([str(ROOT / "examples/contracts/clean_join")])
    assert code == 0
    assert "Status: PASSED" in capsys.readouterr().out


def test_cli_failure_and_json_output(tmp_path: Path):
    output = tmp_path / "report.json"
    audit = tmp_path / "audit.json"
    code = main(
        [
            str(ROOT / "examples/contracts/failing_join"),
            "--format",
            "json",
            "--output",
            str(output),
            "--audit-output",
            str(audit),
        ]
    )
    assert code == 1
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "failed"
    assert json.loads(audit.read_text(encoding="utf-8"))["validator"]["name"] == "acdm-validator"


def test_cli_load_error_returns_two(tmp_path: Path, capsys):
    code = main([str(tmp_path / "missing")])
    assert code == 2
    assert "does not exist" in capsys.readouterr().err
