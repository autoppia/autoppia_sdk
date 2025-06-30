from typing import Dict, Optional, Any, Type
import logging
import importlib
from autoppia.src.apps.interface import AIApp, AppConfig
from autoppia.src.apps.base_app import BaseAIApp
from autoppia.src.apps.adapter import AIAppConfigAdapter
from autoppia.src.apps.app_user_conf_service import AppUserConfService
from autoppia.src.workers.interface import AIWorker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AppFactory")


class AppFactory:
    """Factory class for creating app instances.
    
    This class provides methods for creating app instances from configurations
    and registering app implementations.
    
    Attributes:
        _app_registry: Dictionary of app implementation classes keyed by app type
    """
    
    _app_registry: Dict[str, Type[AIApp]] = {}
    
    @classmethod
    def register_app_class(cls, app_type: str, app_class: Type[AIApp]) -> None:
        """Register an app implementation class for a specific app type.
        
        Args:
            app_type: The type of app (e.g., "chatbot", "assistant", etc.)
            app_class: The app implementation class
        """
        cls._app_registry[app_type] = app_class
        logger.info(f"Registered app class for type: {app_type}")
    
    @classmethod
    def create_app_from_config(cls, app_config: AppConfig, worker_instances: Optional[Dict[str, AIWorker]] = None) -> AIApp:
        """Create an app instance from a configuration.
        
        Args:
            app_config: The app configuration
            worker_instances: Optional dictionary of worker instances to register with the app
            
        Returns:
            AIApp: The created app instance
            
        Raises:
            ValueError: If the app type is not registered
        """
        app_type = app_config.app_type or "base"
        
        # Get the app implementation class
        app_class = cls._app_registry.get(app_type)
        
        if not app_class:
            if app_type == "base":
                app_class = BaseAIApp
            else:
                logger.warning(f"App type {app_type} not registered, using BaseAIApp")
                app_class = BaseAIApp
        
        # Create the app instance
        app = app_class(app_config)
        
        # Register worker instances if provided
        if worker_instances:
            for worker_name, worker in worker_instances.items():
                app.register_worker(worker_name, worker)
        
        return app
    
    @classmethod
    def create_app_from_id(cls, app_id: int) -> AIApp:
        """Create an app instance from an app ID.
        
        Args:
            app_id: The ID of the app to create
            
        Returns:
            AIApp: The created app instance
            
        Raises:
            ValueError: If the app ID is invalid or the app type is not registered
        """
        # Retrieve the app configuration
        app_service = AppUserConfService()
        app_config_dto = app_service.retrieve_app_config(app_id)
        
        # Retrieve the worker configurations
        worker_configs = app_service.retrieve_app_workers(app_id)
        
        # Create the app configuration
        adapter = AIAppConfigAdapter(app_id=str(app_id))
        app_config = adapter.from_autoppia_user_backend(app_config_dto, worker_configs)
        
        # Create worker instances
        # In a real implementation, this would use a worker factory
        # For now, we'll just use empty placeholders
        worker_instances = {}
        
        # Create the app instance
        return cls.create_app_from_config(app_config, worker_instances)
    
    @classmethod
    def load_app_classes(cls) -> None:
        """Load app implementation classes from the registry.
        
        This method attempts to import app implementation modules and register
        their app classes. It looks for modules in the 'autoppia_sdk.src.apps.implementations'
        package.
        """
        try:
            # Import the implementations package
            implementations = importlib.import_module("autoppia_sdk.src.apps.implementations")
            
            # Get the list of implementation modules
            implementation_modules = getattr(implementations, "__all__", [])
            
            for module_name in implementation_modules:
                try:
                    # Import the implementation module
                    module = importlib.import_module(f"autoppia_sdk.src.apps.implementations.{module_name}")
                    
                    # Look for app classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        # Check if the attribute is a class that inherits from AIApp
                        if isinstance(attr, type) and issubclass(attr, AIApp) and attr != AIApp:
                            # Get the app type from the class
                            app_type = getattr(attr, "APP_TYPE", None)
                            
                            if app_type:
                                # Register the app class
                                cls.register_app_class(app_type, attr)
                            else:
                                logger.warning(f"App class {attr_name} in module {module_name} has no APP_TYPE attribute")
                
                except ImportError as e:
                    logger.error(f"Error importing implementation module {module_name}: {e}")
                except Exception as e:
                    logger.error(f"Error loading app classes from module {module_name}: {e}")
        
        except ImportError:
            logger.warning("No app implementations package found")
        except Exception as e:
            logger.error(f"Error loading app classes: {e}")
