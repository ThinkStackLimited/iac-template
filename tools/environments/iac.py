import argparse
import json
import logging
import os
import subprocess

import boto3
import yaml
from yaml.scanner import ScannerError

logger = logging.getLogger("environments")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
required_args = ["env"]
TG_ENV_VARS = []


class RequiredArgMissing(Exception):
    pass


def set_log_level(level):
    logger.setLevel(level)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Infrastructure as Code for Zalando Wholesale Transfer"
    )
    parser.add_argument(
        "-e", "--environment", action="store", help="Environment to build", dest="env"
    )
    parser.add_argument(
        "-a",
        "--apply",
        action="store_true",
        help="Deploy the IaC changes",
        required=False,
    )
    parser.add_argument(
        "-b",
        "--bootstrap",
        action="store_true",
        help="Deploy the IaC required to seed an environment",
        required=False,
    )
    parser.add_argument(
        "-c",
        "--component",
        action="append",
        help="(optional) Components filter: Specify each one separately e.g -c api -c store",
        required=False,
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="(optional) Prevent the running of terragrunt and simply output the intended run",
        required=False,
    )
    parser.add_argument(
        "-r",
        "--component-root",
        action="append",
        help="(optional) Component root filter: Specify each component root separately e.g -r core -r common",
        dest="component_roots",
        required=False,
    )
    parser.add_argument(
        "--retries",
        action="store",
        type=int,
        help="(optional) Number of times to retry processing each component",
        default=0,
        required=False,
    )
    parser.add_argument(
        "--role-arn",
        action="store",
        dest="role_arn",
        help="(optional) Provide the arn of an IAM role to assume before running terragrunt",
        required=False,
    )
    args, pass_through_args = parser.parse_known_args()
    args.pass_through_args = pass_through_args

    return args


def process_missing_arg(arg):
    msg = "Required argument: {} is missing".format(arg)
    logger.error(msg)
    raise RequiredArgMissing(msg)


def load_environment_configuration(path):
    try:
        open(path, "r")
    except FileNotFoundError:
        logger.error(f"Missing expected configuration - {path} does not exist.")
        raise
    else:
        with open(path, "r") as accounts_file:
            try:
                # Use the FullLoader class as we use Aliases and Anchors
                config = yaml.full_load(accounts_file)
            except ScannerError:
                logger.error(f"{path} is not valid yaml.")
                raise

    return config


def convert_yaml_to_env(yaml_to_process):
    TG_ENV_VARS.clear()

    # Convert all the YAML key values into TG_ formatted environment variables
    for item in yaml_to_process:
        env_var = f"TG_{item}".upper()
        env_var_value = yaml_to_process.get(item)
        set_env_var(env_var, env_var_value)


def set_env_var(env_var, env_var_value):
    if type(env_var_value) in (dict, list):
        env_var_value = json.dumps(env_var_value)
    elif type(env_var_value) is bool:
        env_var_value = str(env_var_value).lower()

    os.putenv(env_var, str(env_var_value))
    TG_ENV_VARS.append(env_var)
    logger.debug(f"{env_var} - {env_var_value}")


def run_bootstrap(cmd_args, config):
    component_builder(cmd_args, config, "bootstrap")


def run_iac(cmd_args, config):
    # Use either component roots passed to args or those defined in config
    component_roots = (
        cmd_args.component_roots
        if cmd_args.component_roots
        else config.get("component_roots")
    )

    # Process each component in turn in this list comprehension
    [
        component_builder(cmd_args, config, component_root)
        for component_root in component_roots
    ]


def component_builder(cmd_args, config, component_root):
    components = get_components_to_process(cmd_args, config, component_root)

    if components is None or not bool(components):
        logger.warning(
            f"\nNo component found for {component_root}: {cmd_args.component}\n"
        )
        return

    for component in components:
        logger.info(f"\nProcessing {component_root}: {component}\n")

        if cmd_args.role_arn:
            assume_iam_role(cmd_args.role_arn)

        yaml_to_process = components.get(component)

        if not type(yaml_to_process) is dict:
            logger.info(f"\n{component_root}: {component} is null, ignoring\n")
            continue

        convert_yaml_to_env(yaml_to_process)

        process_args = construct_run_array(
            cmd_args, f"components/{component_root}/{component}"
        )

        process_component(
            cmd_args, process_args, f"{component_root}/{component}", cmd_args.retries
        )
        if TG_ENV_VARS:
            [os.unsetenv(env_var) for env_var in TG_ENV_VARS]


def get_components_to_process(cmd_args, config, component_root):
    components = config.get(cmd_args.env).get(component_root)
    if components:
        if cmd_args.component:
            # filter list of components to provided component list from arguments
            components = {
                key: value
                for key, value in components.items()
                if key in cmd_args.component
            }

    return components


def process_component(cmd_args, process_args, component, retries=0):
    try:
        if cmd_args.debug:  # or "pytest" in sys.modules:
            logger.info(str(process_args))
        else:
            subprocess.run(process_args, check=True)
    except subprocess.CalledProcessError:
        logger.error(f"\nError encountered in {component}\n")
        if retries > 0:
            process_component(cmd_args, process_args, component, retries - 1)
        else:
            exit(1)


def assume_iam_role(role_arn):  # pragma: no cover
    logger.debug(role_arn)
    sts_client = boto3.client("sts")
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn, RoleSessionName="TerragruntSession"
    )
    credentials = assumed_role_object["Credentials"]
    os.putenv("AWS_ACCESS_KEY_ID", credentials["AccessKeyId"])
    os.putenv("AWS_SECRET_ACCESS_KEY", credentials["SecretAccessKey"])
    os.putenv("AWS_SESSION_TOKEN", credentials["SessionToken"])


def construct_run_array(cmd_args, work_dir, *args):
    run_array = ["terragrunt", "--terragrunt-working-dir", work_dir, *args]

    if cmd_args.apply:
        run_array.insert(1, "apply")
        run_array.insert(2, "-auto-approve")
    else:
        run_array.insert(1, "plan")
        run_array.insert(2, "-out=terraform.out")

    return run_array


def main():  # pragma: no cover
    args = parse_args()

    # validate expected arguments have been supplied. Allows for easier testing
    [process_missing_arg(arg) for arg in required_args if getattr(args, arg) is None]

    env_config = load_environment_configuration("./.env-config.yaml")
    convert_yaml_to_env(env_config.get(args.env).get("inputs"))

    if bool(args.bootstrap):
        run_bootstrap(args, env_config)
    else:
        run_iac(args, env_config)


if __name__ == "__main__":  # pragma: no cover
    main()
