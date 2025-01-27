import argparse
from cvid.commands.use import UseCommand
from cvid.commands.build import BuildCommand
from cvid.commands.push import PushCommand
from cvid.commands.cluster import ClusterCommand
from cvid.commands.jobs import JobsCommand
from cvid.commands.aws_registry_login import AWSRegistryLoginCommand
from cvid.commands.cronjobs import CronJobsCommand
from cvid.commands.collect_tasks import CollectTasksCommand
from cvid.commands.models import ModelsCommand
from cvid.commands.paper_matrices import PaperMatricesCommand
from cvid.commands.release import ReleaseCommand
from cvid.commands.version import VersionCommand
from cvid.commands.register import RegisterCommand
from cvid.commands.configure_k8s import ConfigureKubernetes
from cvid.commands.data import DataCommand
from cvid.commands.share_config import ShareConfigCommand
from cvid.commands.resources import ResourcesCommand
import json
from os.path import join, dirname, realpath
import os

from .utils.dict_utils import DictUtils


def main():
    config_path = join(os.getcwd(), 'cvid-config.json')
    if not os.path.exists(config_path):
        print("No cvid-config.json found in current working directory")
        exit(1)

    default_config_path = join(dirname((realpath(__file__))), 'defaults.json')

    with open(config_path, 'r') as config, open(default_config_path, 'r') as default:
        defaults = json.load(default)
        config = json.load(config)
        user_config = config
        config = DictUtils.merge_dicts(defaults, config)
        for key in config['envs'].keys():
            config['envs'][key] = DictUtils.merge_dicts(config['env-defaults'], config['envs'][key])

    args = {'config': config, 'user_config': user_config}
    commands = [UseCommand(**args), BuildCommand(**args), PushCommand(**args),
                ClusterCommand(**args), JobsCommand(**args), AWSRegistryLoginCommand(**args),
                CronJobsCommand(**args), CollectTasksCommand(**args), ReleaseCommand(**args), VersionCommand(**args),
                ConfigureKubernetes(**args), RegisterCommand(**args),
                ModelsCommand(**args), PaperMatricesCommand(**args), ShareConfigCommand(**args),
                ModelsCommand(**args), PaperMatricesCommand(**args), ResourcesCommand(**args), DataCommand(**args)]

    parser = argparse.ArgumentParser(prog='cvid')
    subparsers = parser.add_subparsers()
    for cmd in commands:
        subparser = subparsers.add_parser(name=cmd.name(), help=cmd.help())
        cmd.add_arguments(subparser)
        subparser.set_defaults(func=cmd.run)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError as e:
        if str(e) == "'Namespace' object has no attribute 'func'":
            parser.print_help()
            parser.exit()
        else:
            raise e

    with open(config_path, 'w') as f:
        json.dump(user_config, f, indent=4)
