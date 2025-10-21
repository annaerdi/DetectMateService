# Quick Start

Get up and running with DetectMate in minutes.

## Prerequisites

- Python 3.12 or higher
- pip or uv package manager

## Installation

```bash
# Install DetectMate Service framework
pip install detectmateservice

# Install the DetectMate library (for components)
pip install detectmatelibrary
```

## Your First Service

### 1. Create Service Settings

Create a file named `settings.yaml`:

```yaml
component_name: my-first-service
component_type: core  # or use a library component like "detectors.RandomDetector"
log_level: INFO
log_dir: ./logs
manager_addr: ipc:///tmp/detectmate.cmd.ipc
engine_addr: ipc:///tmp/detectmate.engine.ipc
```

### 2. Start the Service

```bash
detectmate start --settings settings.yaml
```

You should see output like:

```
[2025-10-21 10:30:00] INFO core.abc123: setup_io: ready to process messages
[2025-10-21 10:30:00] INFO core.abc123: Manager listening on ipc:///tmp/detectmate.cmd.ipc
[2025-10-21 10:30:00] INFO core.abc123: engine started
```

### 3. Check Service Status

In another terminal:

```bash
detectmate status --settings settings.yaml
```

Output:

```json
{
  "status": {
    "component_type": "core",
    "component_id": "abc123...",
    "running": true
  },
  "settings": {
    "component_name": "my-first-service",
    "log_level": "INFO",
    ...
  },
  "configs": {}
}
```

### 4. Stop the Service

```bash
detectmate stop --settings settings.yaml
```

## Using a Library Component

### 1. Update Settings

Modify `settings.yaml` to use a library component:

```yaml
component_name: random-detector
component_type: detectors.RandomDetector
component_config_class: detectors.RandomDetectorConfig
config_file: detector-config.yaml
log_level: INFO
manager_addr: ipc:///tmp/detectmate.cmd.ipc
engine_addr: ipc:///tmp/detectmate.engine.ipc
```

### 2. Create Component Configuration

Create `detector-config.yaml`:

```yaml
threshold: 0.75
window_size: 10
enabled: true
```

### 3. Start with Configuration

```bash
detectmate start --settings settings.yaml --config detector-config.yaml
```

### 4. Reconfigure at Runtime

Create `new-config.yaml`:

```yaml
threshold: 0.85
window_size: 15
enabled: true
```

Apply the changes:

```bash
# Apply without saving to file
detectmate reconfigure --settings settings.yaml --config new-config.yaml

# Apply and persist to file
detectmate reconfigure --settings settings.yaml --config new-config.yaml --persist
```

## Next Steps

- Learn about [Configuration Options](configuration.md)
