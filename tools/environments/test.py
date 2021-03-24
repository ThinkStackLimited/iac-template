import logging
import subprocess
import sys
from unittest import mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from yaml.scanner import ScannerError

import tools.environments.iac as iac
from tools.environments.iac import RequiredArgMissing


@pytest.fixture(scope="function")
def session_log(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def remove_sysv_args():
    sys.argv.pop()


def test_validate_args_missing():
    with pytest.raises(RequiredArgMissing):
        iac.main()


def test_validate_args(caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--env=root")
    sys.argv.append("--debug")
    iac.main()

    assert caplog.records[0].msg == 'TG_ENVIRONMENTS - {"root": "649115683993"}'
    index = 0
    for component in ["resource_groups"]:
        assert caplog.records[index + 1].msg == f"\nProcessing bootstrap: {component}\n"
        assert (
            caplog.records[index + 2].msg
            == f"['terragrunt', 'plan', '-out=terraform.out', "
            f"'--terragrunt-working-dir', 'components/bootstrap/{component}']"
        )
        index += 2


@mock.patch("subprocess.run")
def test_iac_no_dry_run(mock_subprocess, caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--env=root")
    iac.main()

    assert caplog.records[0].msg == 'TG_ENVIRONMENTS - {"root": "649115683993"}'
    assert caplog.records[1].msg == "\nProcessing bootstrap: resource_groups\n"


@mock.patch("subprocess.run")
def test_iac_no_dry_run_exception(mock_subproc_run, caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--env=root")

    mock_subproc_run.side_effect = subprocess.CalledProcessError(1, "2")

    with pytest.raises(SystemExit):
        iac.main()


@mock.patch("subprocess.run")
def test_iac_no_dry_run_exception_with_retries(mock_subproc_run, caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--env=root")
    sys.argv.append("--retries=1")

    mock_subproc_run.side_effect = subprocess.CalledProcessError(1, "2")

    with pytest.raises(SystemExit):
        iac.main()


@mock.patch("subprocess.run")
def test_iac_apply(mock_subproc_run, caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--env=root")
    sys.argv.append("--debug")
    sys.argv.append("--apply")

    iac.main()

    assert caplog.records[0].msg == 'TG_ENVIRONMENTS - {"root": "649115683993"}'
    assert caplog.records[1].msg == "\nProcessing bootstrap: resource_groups\n"
    assert (
        caplog.records[2].msg
        == "['terragrunt', 'apply', '-auto-approve', '--terragrunt-working-dir', "
        "'components/bootstrap/resource_groups']"
    )


def test_invalid_component_root(caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--env=root")
    sys.argv.append("--debug")
    sys.argv.append("--component-root=test")
    iac.main()

    assert caplog.records[0].msg == 'TG_ENVIRONMENTS - {"root": "649115683993"}'
    assert caplog.records[1].msg == "\nNo component found for test: None\n"


@patch("boto3.client")
def test_role_arn(mock_client, caplog):
    iac.set_log_level("DEBUG")
    sys.argv.append("--environment=root")
    sys.argv.append("--debug")
    sys.argv.append("--component-root=bootstrap")
    sys.argv.append("--component=resource_groups")
    sys.argv.append("--role-arn=arn:aws:iam::123456789012:role/accounts3access")
    mock_client().assume_role.return_value = {
        "AssumedRoleUser": {
            "AssumedRoleId": "AROA3XFRBF535PLBIFPI4:s3-access-example",
            "Arn": "arn:aws:sts::123456789012:assumed-role/accounts3access/s3-access-example",
        },
        "Credentials": {
            "SecretAccessKey": "9drTJvcXLB89EXAMPLELB8923FB892xMFI",
            "SessionToken": "AQoXdzELDDY//////////wEaoAK1wvxJY12r2IrDFT2IvAzTCn3zHoZ7YNtpiQLF0MqZye/qwjzP2iEXAMPLEbw"
            "/m3hsj8VBTkPORGvr9jM5sgP+w9IZWZnU+LWhmg"
            "+a5fDi2oTGUYcdg9uexQ4mtCHIHfi4citgqZTgco40Yqr4lIlo4V2b2Dyauk0eYFNebHtYlFVgAUj"
            "+7Indz3LU0aTWk1WKIjHmmMCIoTkyYp/k7kUG7moeEYKSitwQIi6Gjn+nyzM"
            "+PtoA3685ixzv0R7i5rjQi0YE0lf1oeie3bDiNHncmzosRM6SFiPzSvp6h/32xQuZsjcypmwsPSDtTPYcs0+YN"
            "/8BRi2/IcrxSpnWEXAMPLEXSDFTAQAM6Dl9zR0tXoybnlrZIwMLlMi1Kcgo5OytwU=",
            "Expiration": "2016-03-15T00:05:07Z",
            "AccessKeyId": "ASIAJEXAMPLEXEG2JICEA",
        },
    }
    iac.main()
    calls = [
        call("sts"),
        call().assume_role(
            RoleArn="arn:aws:iam::123456789012:role/accounts3access",
            RoleSessionName="TerragruntSession",
        ),
    ]
    mock_client.assert_has_calls(calls, any_order=False)


def test_invalid_component_configuration(caplog):
    sys.argv.append("--environment=invalid-component")

    args = iac.parse_args()
    env_config = iac.load_environment_configuration(
        "./tools/environments/test_config/invalid_component.yaml"
    )
    iac.run_iac(args, env_config)
    assert caplog.records[0].msg == "\nProcessing bootstrap: resource_groups\n"
    assert caplog.records[1].msg == "\nbootstrap: resource_groups is null, ignoring\n"


def test_valid_setting_of_env_vars(caplog):
    sys.argv.append("--environment=valid-env-vars")

    args = iac.parse_args()
    env_config = iac.load_environment_configuration(
        "./tools/environments/test_config/valid_env_vars.yaml"
    )
    iac.convert_yaml_to_env(env_config.get(args.env).get("inputs"))
    assert iac.TG_ENV_VARS[1] == "TG_TEST_TRUE"
    assert iac.TG_ENV_VARS[2] == "TG_TEST_FALSE"


def test_missing_environment_configuration(caplog):
    with pytest.raises(FileNotFoundError):
        iac.load_environment_configuration(
            "./tools/environments/test_config/nofile.yaml"
        )
    assert (
        caplog.records[0].msg
        == "Missing expected configuration - ./tools/environments/test_config/nofile.yaml does not exist."
    )


def test_invalid_environment_configuration(caplog):
    with pytest.raises(ScannerError):
        iac.load_environment_configuration(
            "./tools/environments/test_config/invalid.yaml"
        )
    assert (
        caplog.records[0].msg
        == "./tools/environments/test_config/invalid.yaml is not valid yaml."
    )
