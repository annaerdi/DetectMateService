# DetectMate Service Framework

Welcome to the DetectMate Service Framework documentation. DetectMate is a flexible, component-based framework for
building distributed detection and processing services.

## Overview

DetectMate provides a foundation for creating services that:

- **Process data in real-time** using a high-performance messaging architecture
- **Support dynamic reconfiguration** without service restarts
- **Enable modular component design** through a plugin-based system
- **Provide command and control** via a simple REQ/REP interface
- **Scale horizontally** with independent service instances

## Key Features

- **Dual-Channel Architecture**: Separate channels for management commands (REQ/REP) and data processing (PAIR)
- **Hot Reconfiguration**: Update service parameters at runtime with optional persistence
- **Component Loader**: Dynamically load processing components from the DetectMate library
- **Type-Safe Configuration**: Pydantic-based settings and configuration validation
- **Flexible Deployment**: Support for IPC and TCP socket protocols
- **Comprehensive Logging**: Built-in logging to console and file with configurable levels

## Documentation Structure

### User Guide

- [Quick Start](user-guide/quick-start.md)
- [Installation](user-guide/installation.md)
- [Configuration](user-guide/configuration.md)

### Developer Guide

TBA

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
