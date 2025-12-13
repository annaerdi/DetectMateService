# DetectMate Service Framework

Welcome to the DetectMate Service Framework documentation. DetectMate is a flexible, component-based framework for
building distributed detection and processing services.

DetectMate Service is a framework for building distributed processing services. It uses NNG's messaging architecture to process data in real-time.

## Key Features

- **Real-time Processing**: Fast data handling using ZeroMQ/NNG.
- **Dynamic Reconfiguration**: Update settings without restarting.
- **Modular**: Load components dynamically.
- **Scalable**: Run multiple independent service instances.

### User Guide

- [Quick Start](quick-start.md)
- [Installation](installation.md)
- [Usage Guide](usage.md): CLI reference
- [Configuration](configuration.md): settings and environment variables

## Quick Example

```yaml
# service-settings.yaml
component_name: my-detector
component_type: detectors.RandomDetector
log_level: INFO
manager_addr: ipc:///tmp/detectmate.cmd.ipc
engine_addr: ipc:///tmp/detectmate.engine.ipc
```

```yaml
# component-config.yaml
threshold: 0.7
window_size: 20
enabled: true
```

```bash
# Start the service
detectmate start --settings service-settings.yaml --config component-config.yaml

# Check status
detectmate status --settings service-settings.yaml

# Reconfigure at runtime
detectmate reconfigure --settings service-settings.yaml --config new-config.yaml

# Stop the service
detectmate stop --settings service-settings.yaml
```
