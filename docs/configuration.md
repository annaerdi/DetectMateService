# Configuration

DetectMate can be configured via a YAML file or environment variables.

## Service settings (`settings.yaml`)

These settings control the service infrastructure.

| Setting | Env Variable | Default | Description |
| :--- | :--- | :--- | :--- |
| `component_name` | `DETECTMATE_COMPONENT_NAME` | `None` | A human-readable name for the service instance. |
| `component_type` | `DETECTMATE_COMPONENT_TYPE` | `core` | The Python class path for the component (e.g., `detectors.MyDetector`). |
| `log_level` | `DETECTMATE_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `log_dir` | `DETECTMATE_LOG_DIR` | `./logs` | Directory for log files. |
| `manager_addr` | `DETECTMATE_MANAGER_ADDR` | `ipc:///tmp/detectmate.cmd.ipc` | Address for management commands (REQ/REP). |
| `engine_addr` | `DETECTMATE_ENGINE_ADDR` | `ipc:///tmp/detectmate.engine.ipc` | Address for data processing (PAIR0/1). |

### Environment Variables

Environment variables override values in the YAML file. They are prefixed with `DETECTMATE_`.

Example:
```bash
export DETECTMATE_LOG_LEVEL=DEBUG
export DETECTMATE_COMPONENT_NAME=worker-1
detectmate start
```

## Component configuration

This configuration is specific to the logic of your component (e.g., thresholds, enabled flags). It is passed via the `--config` flag.

```yaml
# detector-config.yaml
threshold: 0.85
sensitivity: high
enabled: true
```
