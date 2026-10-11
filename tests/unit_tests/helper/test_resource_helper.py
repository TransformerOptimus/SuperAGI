from unittest.mock import patch, MagicMock

from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.resource import Resource


def test_make_written_file_resource(mocker):
    mocker.patch('os.getcwd', return_value='/')
    mocker.patch('os.makedirs', return_value=None)
    mocker.patch('os.path.getsize', return_value=1000)
    mocker.patch('os.path.splitext', return_value=("", ".txt"))
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['FILE', '/', '/', 'FILE'])
    mock_agent = Agent(id=1, name='TestAgent')
    mock_agent_execution = AgentExecution(id=1, name='TestExecution')
    session = MagicMock()

    with patch('superagi.helper.resource_helper.logger') as logger_mock:
        session.query.return_value.filter_by.return_value.first.return_value = None
        # Create a Resource object
        resource = Resource(
            name='test.txt',
            path='/test.txt',
            storage_type='FILE',
            size=1000,
            type='application/txt',
            channel='OUTPUT',
            agent_id=1,
            agent_execution_id=1
        )

        # Mock the session.add() method to return the created Resource object
        session.add.return_value = resource
        result = ResourceHelper.make_written_file_resource('test.txt', mock_agent, mock_agent_execution, session)

    assert result.name == 'test.txt'
    assert result.path == '/test.txt'
    assert result.storage_type == 'FILE'
    assert result.size == 1000
    assert result.type == 'application/txt'
    assert result.channel == 'OUTPUT'
    assert result.agent_id == 1


def test_get_resource_path(mocker):
    mocker.patch('os.getcwd', return_value='/')
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['/'])

    result = ResourceHelper.get_resource_path('test.txt')

    assert result == '/test.txt'


def test_get_agent_resource_path(mocker):
    mocker.patch('os.getcwd', return_value='/')
    mocker.patch('os.makedirs')
    mocker.patch('superagi.helper.resource_helper.get_config', side_effect=['/'])
    mock_agent = Agent(id=1, name='TestAgent')
    mock_agent_execution = AgentExecution(id=1, name='TestExecution')
    result = ResourceHelper.get_agent_write_resource_path('test.txt', mock_agent, mock_agent_execution)

    assert result == '/test.txt'


def test_get_formatted_agent_level_path():
    agent = Agent(id=1, name="TestAgent")
    path = "/data/{agent_id}/file.txt"
    formatted_path = ResourceHelper.get_formatted_agent_level_path(agent, path)
    expected_path = "/data/TestAgent_1/file.txt"
    assert formatted_path == expected_path


def test_get_formatted_agent_execution_level_path():
    agent_execution = AgentExecution(id=1, name="TestExecution")
    path = "/results/{agent_execution_id}/output.csv"
    formatted_path = ResourceHelper.get_formatted_agent_execution_level_path(agent_execution, path)
    expected_path = "/results/TestExecution_1/output.csv"
    assert formatted_path == expected_path


# --- Path traversal regression tests ---
# Failure modes covered:
#   1. ".." segments in the file name.
#   2. Sibling directory with the same prefix (/base vs /base2).
#   3. Symlink inside the root that points outside the root.
#   4. Absolute file name.
#   5. NUL byte in the file name.
#   6. Root directory "/" (the check must not reject valid paths).
#   7. Agent or run names with "/", "\" or ".." expand into the path template.
#      This applies to the read path and to the write path.

import os

import pytest


def _patch_config(mocker, input_root, output_root):
    values = {
        'RESOURCES_INPUT_ROOT_DIR': input_root,
        'RESOURCES_OUTPUT_ROOT_DIR': output_root,
        'STORAGE_TYPE': 'FILE',
    }
    mocker.patch('superagi.helper.resource_helper.get_config',
                 side_effect=lambda key, default=None: values.get(key, default))


@pytest.mark.parametrize("file_name", [
    "../escape.txt",
    "a/../../escape.txt",
    "../output2/escape.txt",
])
def test_validate_path_containment_rejects_dotdot(tmp_path, file_name):
    root = tmp_path / "output"
    root.mkdir()
    (tmp_path / "output2").mkdir()
    with pytest.raises(ValueError):
        ResourceHelper._validate_path_containment(str(root) + "/", file_name)


def test_validate_path_containment_rejects_prefix_sibling(tmp_path):
    root = tmp_path / "base"
    root.mkdir()
    (tmp_path / "base2").mkdir()
    # Root without a trailing slash: "/base" + "2/x" must not pass.
    with pytest.raises(ValueError):
        ResourceHelper._validate_path_containment(str(root), "2/x.txt")


def test_validate_path_containment_rejects_symlink_escape(tmp_path):
    root = tmp_path / "output"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    os.symlink(str(outside), str(root / "link"))
    with pytest.raises(ValueError):
        ResourceHelper._validate_path_containment(str(root) + "/", "link/secret.txt")


def test_validate_path_containment_rejects_nul_byte(tmp_path):
    with pytest.raises(ValueError):
        ResourceHelper._validate_path_containment(str(tmp_path) + "/", "a\x00b.txt")


def test_validate_path_containment_absolute_name_stays_inside_root(tmp_path):
    root = str(tmp_path) + "/"
    result = ResourceHelper._validate_path_containment(root, "/etc/passwd")
    assert result.startswith(str(tmp_path) + os.sep)


def test_validate_path_containment_accepts_valid_paths(tmp_path):
    root = str(tmp_path) + "/"
    assert ResourceHelper._validate_path_containment(root, "sub/file.txt") == str(tmp_path / "sub" / "file.txt")
    assert ResourceHelper._validate_path_containment(root, "") == str(tmp_path)


def test_validate_path_containment_accepts_filesystem_root():
    assert ResourceHelper._validate_path_containment("/", "test.txt") == "/test.txt"


@pytest.mark.parametrize("name", ["../../escape", "..\\..\\escape", "a/b", "..", "/abs", "x\x00y"])
def test_formatted_agent_level_path_has_no_separators(name):
    agent = Agent(id=1, name=name)
    formatted = ResourceHelper.get_formatted_agent_level_path(agent, "base/{agent_id}/")
    component = formatted[len("base/"):-1]
    assert "/" not in component
    assert "\\" not in component
    assert "\x00" not in component
    assert component not in ("", ".", "..")


@pytest.mark.parametrize("name", ["../../escape", "..\\..\\escape", "a/b", "..", "/abs", "x\x00y"])
def test_formatted_agent_execution_level_path_has_no_separators(name):
    agent_execution = AgentExecution(id=2, name=name)
    formatted = ResourceHelper.get_formatted_agent_execution_level_path(agent_execution, "base/{agent_execution_id}/")
    component = formatted[len("base/"):-1]
    assert "/" not in component
    assert "\\" not in component
    assert "\x00" not in component
    assert component not in ("", ".", "..")


def test_write_path_stays_under_configured_base_with_hostile_names(tmp_path, mocker):
    base = tmp_path / "workspace" / "output"
    base.mkdir(parents=True)
    _patch_config(mocker, str(tmp_path / "in"), str(base) + "/{agent_id}/{agent_execution_id}")
    agent = Agent(id=1, name="../../../escape")
    execution = AgentExecution(id=2, name="../../escape")

    path = ResourceHelper.get_agent_write_resource_path("out.txt", agent, execution)

    assert os.path.commonpath([os.path.realpath(path), str(base)]) == str(base)
    assert not (tmp_path / "escape").exists()
    assert not (tmp_path.parent / "escape").exists()


def test_read_path_stays_under_configured_base_with_hostile_names(tmp_path, mocker):
    in_base = tmp_path / "workspace" / "input"
    out_base = tmp_path / "workspace" / "output"
    in_base.mkdir(parents=True)
    out_base.mkdir(parents=True)
    _patch_config(mocker, str(in_base) + "/{agent_id}", str(out_base) + "/{agent_id}/{agent_execution_id}")
    agent = Agent(id=1, name="../../../escape")
    execution = AgentExecution(id=2, name="../../escape")

    path = ResourceHelper.get_agent_read_resource_path("in.txt", agent, execution)

    allowed = (str(in_base), str(out_base))
    assert any(os.path.commonpath([os.path.realpath(path), base]) == base for base in allowed)


def test_read_path_rejects_file_name_traversal(tmp_path, mocker):
    in_base = tmp_path / "workspace" / "input"
    out_base = tmp_path / "workspace" / "output"
    in_base.mkdir(parents=True)
    out_base.mkdir(parents=True)
    _patch_config(mocker, str(in_base) + "/{agent_id}", str(out_base) + "/{agent_id}/{agent_execution_id}")
    agent = Agent(id=1, name="TestAgent")
    execution = AgentExecution(id=2, name="TestExecution")

    with pytest.raises(ValueError):
        ResourceHelper.get_agent_read_resource_path("../../../../etc/passwd", agent, execution)


def test_read_path_revalidates_after_placeholder_expansion(tmp_path, mocker):
    in_base = tmp_path / "workspace" / "input"
    out_base = tmp_path / "workspace" / "output"
    in_base.mkdir(parents=True)
    out_base.mkdir(parents=True)
    _patch_config(mocker, str(in_base) + "/{agent_id}", str(out_base) + "/{agent_id}/{agent_execution_id}")
    agent = Agent(id=1, name="TestAgent")
    execution = AgentExecution(id=2, name="TestExecution")
    # A symlink at the expanded agent directory points outside the output base.
    outside = tmp_path / "outside"
    outside.mkdir()
    os.symlink(str(outside), str(out_base / "TestAgent_1"))

    with pytest.raises(ValueError):
        ResourceHelper.get_agent_read_resource_path("in.txt", agent, execution)
    with pytest.raises(ValueError):
        ResourceHelper.get_agent_write_resource_path("out.txt", agent, execution)
