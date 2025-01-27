from cvid.commands.abstract.with_services import CommandWithServices


class BuildCommand(CommandWithServices):
    def run(self, args):
        super().run(args)

        # Make the common shared libraries
        self.run_shell_command("cd collabovid-shared; make")
        self.run_shell_command("cd collabovid-store; make")

        service_names = [service for service, _ in args.services]
        if "web" in service_names:
            self.run_shell_command("cd web; python manage.py collectstatic --noinput")

        if "search" in service_names or "web" in service_names:
            # First build the collabovid base image where search and web depend upon
            self.run_shell_command(
                "DOCKER_BUILDKIT=1 docker buildx build --platform linux/amd64 -t collabovid-base -f docker/collabovid-base.Dockerfile .")

        # Build all services with docker buildkit enabled and tag them with an automatically generated tag
        for service, config in args.services:
            self.print_info("Building service: {}".format(service))
            tag = self.generate_tag()
            image = f"{service}:{tag}"
            self.run_shell_command(f"DOCKER_BUILDKIT=1 docker buildx build --platform linux/amd64 -t {image} -f docker/{service}.Dockerfile .")

            # delete/untag all old images from that service
            if args.delete_old:
                result = self.run_shell_command(
                    f"docker image ls --filter reference=\"*/{service}\" --filter reference=\"{service}\" --format '{{{{.Repository}}}}:{{{{.Tag}}}}' | grep -v '...:{tag}'",
                    quiet=True, exit_on_fail=False, collect_output=True, print_command=False)
                if result.returncode == 0:
                    for output in result.stdout.decode('utf8').strip().split('\n'):
                        if len(output) > 0:
                            self.run_shell_command(f"docker rmi {output}")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--delete-old', action='store_true')

    def help(self):
        return "Build a repository and tag it with the current version."

    def name(self):
        return "build"
