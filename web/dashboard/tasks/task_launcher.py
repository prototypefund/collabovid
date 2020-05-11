from dashboard.tasks.kube_job_utils import create_job_object, run_job, id_generator
import os
from os.path import join
from django.conf import settings
import subprocess


class TaskLauncher():
    def launch_task(self, name, config):
        raise NotImplementedError

    def _generate_command(self, name, config, username, full_path=True):

        service = config['service']

        if full_path:
            script_path = join(settings.BASE_DIR, '..', service, 'run_task.py')
        else:
            script_path = 'run_task.py'

        parameter_values = []

        for param, param_type, value in config['parameters']:

            if param_type == 'bool':
                if value == '1':
                    parameter_values.append("--{}".format(param))
            else:
                parameter_values.append("--{} {}".format(param, value))

        return "python {} -u {} {} {}".format(script_path, username, name, " ".join(parameter_values))

secret_map = {
    'scrape': ['scrape', 'shared'],
    'web': ['web', 'shared'],
    'search': ['search', 'shared']
}


class KubeTaskLauncher(TaskLauncher):
    def launch_task(self, name, config):
        repository = config['repository']
        registry = os.getenv('REGISTRY', 'localhost:32000')
        if len(registry) > 0:
            registry += '/'
        version = '0.0.0'
        image = registry + repository + ':' + version
        cmd = self._generate_command(name, config, 'web', full_path=False)

        job_object = create_job_object(name=name + '-' + id_generator(size=10), container_image=image,
                                       command=["bash", "-c"],
                                       args=["export PYTHONPATH=/app:$PYTHONPATH && " + cmd],
                                       secret_names=secret_map[repository])
        run_job(job_object)


class LocalTaskLauncher(TaskLauncher):
    def launch_task(self, name, config):

        launch_env = os.environ.copy()
        launch_env.pop("DJANGO_SETTINGS_MODULE")

        cmd = self._generate_command(name, config, 'web')

        print(cmd)

        subprocess.Popen(cmd, shell=True, env=launch_env)
