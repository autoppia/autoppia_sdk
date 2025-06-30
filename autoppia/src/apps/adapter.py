from typing import Dict, Optional, Any, List
from autoppia_backend_client.models import WorkerConfig as WorkerConfigDTO
from autoppia.src.workers.adapter import AIWorkerConfigAdapter
from autoppia.src.workers.interface import AIWorker
from autoppia.src.apps.interface import AppConfig


class AIAppConfigAdapter(AIWorkerConfigAdapter):
    """Adapter for constructing app configurations from backend DTOs.
    
    Extends AIWorkerConfigAdapter to handle app-specific configuration parameters.
    
    Args:
        app_id: Optional identifier for app instance tracking
    """
    
    def __init__(self, app_id: Optional[str] = None) -> None:
        super().__init__(worker_id=app_id)
        self.app_id = app_id
        self.app_config_dto: Optional[WorkerConfigDTO] = None
        self.worker_adapters: Dict[str, AIWorkerConfigAdapter] = {}
    
    def adapt_workers(self, worker_configs: Dict[str, WorkerConfigDTO]) -> Dict[str, AIWorker]:
        """Adapt worker configurations from backend DTOs.
        
        Args:
            worker_configs: Dictionary of worker configuration DTOs keyed by worker name
            
        Returns:
            Dictionary of initialized worker instances keyed by worker name
            
        Raises:
            ValueError: If required worker configuration is missing
        """
        workers = {}
        
        for worker_name, worker_config_dto in worker_configs.items():
            adapter = AIWorkerConfigAdapter(worker_id=worker_config_dto.id)
            worker_config = adapter.from_autoppia_user_backend(worker_config_dto)
            
            # Store the adapter for later use
            self.worker_adapters[worker_name] = adapter
            
            # Create the worker instance (this would require a factory or registry)
            # For now, we'll just store the configuration
            workers[worker_name] = worker_config
        
        return workers
    
    def adapt_ui_config(self) -> Dict[str, Any]:
        """Adapt UI configuration from backend DTO.
        
        Returns:
            Dictionary of UI configuration parameters
        """
        if not self.app_config_dto or not self.app_config_dto.extra_arguments:
            return {}
        
        return self.app_config_dto.extra_arguments.get("ui_config", {})
    
    def adapt_permissions(self) -> List[str]:
        """Adapt permissions from backend DTO.
        
        Returns:
            List of permission strings
        """
        if not self.app_config_dto or not self.app_config_dto.extra_arguments:
            return []
        
        return self.app_config_dto.extra_arguments.get("permissions", [])
    
    def adapt_metadata(self) -> Dict[str, Any]:
        """Adapt metadata from backend DTO.
        
        Returns:
            Dictionary of metadata parameters
        """
        if not self.app_config_dto or not self.app_config_dto.extra_arguments:
            return {}
        
        return self.app_config_dto.extra_arguments.get("metadata", {})
    
    def from_autoppia_user_backend(
        self, app_config_dto: WorkerConfigDTO, worker_configs: Dict[str, WorkerConfigDTO] = None
    ) -> AppConfig:
        """Construct app configuration from backend DTO with validation.
        
        Args:
            app_config_dto: Source data transfer object from backend
            worker_configs: Dictionary of worker configuration DTOs keyed by worker name
            
        Returns:
            AppConfig: Initialized app configuration with integrated services and workers
            
        Raises:
            ValueError: For missing required fields or invalid configurations
            RuntimeError: If service initialization fails
        """
        self.app_config_dto = app_config_dto
        
        # First, use the parent class to adapt the basic worker configuration
        worker_config = super().from_autoppia_user_backend(app_config_dto)
        
        # Then, adapt app-specific configuration
        workers = self.adapt_workers(worker_configs or {})
        ui_config = self.adapt_ui_config()
        permissions = self.adapt_permissions()
        metadata = self.adapt_metadata()
        app_type = app_config_dto.extra_arguments.get("app_type") if app_config_dto.extra_arguments else None
        
        # Create the app configuration
        return AppConfig(
            name=worker_config.name,
            system_prompt=worker_config.system_prompt,
            ip=worker_config.ip,
            port=worker_config.port,
            integrations=worker_config.integrations,
            llms=worker_config.llms,
            vectorstores=worker_config.vectorstores,
            extra_arguments=worker_config.extra_arguments,
            workers=workers,
            app_type=app_type,
            ui_config=ui_config,
            permissions=permissions,
            metadata=metadata
        )
