import argparse
from typing import Optional
from pathlib import Path

from .settings import ServiceSettings
from .core import Service


def start_service(settings_path: Path, params_path: Optional[Path] = None):
    """Start the service with given settings and parameters."""
    settings = ServiceSettings.from_yaml(settings_path)
    service = Service(settings=settings)
    try:
        with service:
            #print(f"Service started with ID: {service.component_id}")
            #print(f"Manager address: {settings.manager_addr}")
            #print(f"Engine address: {settings.engine_addr}")
            service.run()
    except KeyboardInterrupt:
        print("Shutting down service...")
        service.stop()

def stop_service(settings_path: Path):
    """Stop a running service."""
    pass

def reconfigure_service(settings_path: Path, params_path: Path):
    """Reconfigure a running service with new parameters."""
    pass

def get_status(settings_path: Path):
    """Get the current status of the service."""
    pass


def main():
    parser = argparse.ArgumentParser(description="DetectMate Service CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the service")
    start_parser.add_argument("--settings", required=True, help="Service settings YAML file")
    start_parser.add_argument("--params", help="Service parameters YAML file")

    # Reconfigure command
    reconfigure_parser = subparsers.add_parser("reconfigure", help="Reconfigure service parameters")
    reconfigure_parser.add_argument("--settings", required=True,
                                    help="Service settings YAML file (to get manager address)")
    reconfigure_parser.add_argument("--params", required=True, help="New parameters YAML file")

    args = parser.parse_args()

    if args.command == "start":
        start_service(args.settings, args.params)
    elif args.command == "reconfigure":
        # TODO: implement reconfigure_service!
        reconfigure_service(args.settings, args.params)


if __name__ == "__main__":
    main()
