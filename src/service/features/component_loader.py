import importlib
from typing import Any, Dict, Type

from detectmatelibrary.common.core import CoreComponent


class ComponentLoader:
    DEFAULT_ROOT = "detectmatelibrary"

    @classmethod
    def load_component(
        cls,
        component_type: str,  # "detectors.RandomDetector" or "pkg.mod.Class"
        config: Dict[str, Any] | None = None,
    ) -> CoreComponent:
        """Load a component from the DetectMate library or from any installed
        package.

        Args:
            component_type: dot path like "detectors.RandomDetector"
                            OR full dot path like "package.module.ClassName"
            config: configuration dictionary for the component

        Returns:
            Initialized component instance
        """
        try:
            # Split path into module + class
            if '.' not in component_type:
                raise ValueError(f"Invalid component type format: {component_type}. "
                                 f"Expected 'module.ClassName or 'package.module.ClassName'")

            module_name, class_name = component_type.rsplit('.', 1)

            # Heuristic: if it looks like a bare module name (no package),
            # treat it as being under detectmatelibrary.*
            if "." not in module_name:
                # e.g. "detectors.RandomDetector" -> "detectmatelibrary.detectors"
                module_path = f"{cls.DEFAULT_ROOT}.{module_name}"
            else:
                # already a full path
                module_path = module_name

            module = importlib.import_module(module_path)
            component_class: Type[CoreComponent] = getattr(module, class_name)

            # create instance with config if provided
            if config:
                instance = component_class(config=config)
            else:
                instance = component_class()

            if not isinstance(instance, CoreComponent):
                raise TypeError(f"Loaded component {component_type} is not a {CoreComponent.__name__}")

            return instance

        except ImportError as e:
            raise ImportError(f"Failed to import component {component_type}: {e}")
        except AttributeError:
            raise AttributeError(f"Component class {class_name} not found in module {module_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to load component {component_type}: {e}")
