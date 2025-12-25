"""
Configuration loader for the LLM routing system.
Loads and validates YAML configuration files with strict Pydantic validation.
"""

import yaml
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    """Configuration for a single model tier."""
    model_name: str
    max_context_tokens: int = Field(gt=0)
    cost_per_token: float = Field(ge=0.0)


class ModelsConfig(BaseModel):
    """Top-level models configuration."""
    models: dict[str, ModelConfig]

    @field_validator('models')
    @classmethod
    def validate_required_tiers(cls, v: dict[str, ModelConfig]) -> dict[str, ModelConfig]:
        """Ensure all required model tiers are present."""
        required_tiers = {'small', 'medium', 'api'}
        missing = required_tiers - v.keys()
        if missing:
            raise ValueError(f"Missing required model tiers: {missing}")
        return v


class RoutingThresholds(BaseModel):
    """Threshold values for routing decisions."""
    small_max_tokens: int = Field(gt=0)
    medium_context_tokens: int = Field(gt=0)
    classifier_confidence_min: float = Field(ge=0.0, le=1.0)


class RoutingRule(BaseModel):
    """A single routing rule with conditions and target."""
    name: str
    condition: dict[str, Any]
    route_to: str

    @field_validator('route_to')
    @classmethod
    def validate_route_target(cls, v: str) -> str:
        """Ensure route target is a valid model tier."""
        valid_tiers = {'small', 'medium', 'api'}
        if v not in valid_tiers:
            raise ValueError(f"Invalid route_to value: {v}. Must be one of {valid_tiers}")
        return v


class RoutingConfig(BaseModel):
    """Top-level routing configuration."""
    thresholds: RoutingThresholds
    rules: list[RoutingRule]


class Config:
    """Global configuration holder."""
    
    def __init__(self, config_dir: Path | str = "config"):
        """
        Load and validate configuration files.
        
        Args:
            config_dir: Path to directory containing YAML files
            
        Raises:
            FileNotFoundError: If config files are missing
            ValueError: If config validation fails
        """
        self.config_dir = Path(config_dir)
        self.models = self._load_models()
        self.routing = self._load_routing()
    
    def _load_yaml(self, filename: str) -> dict:
        """Load and parse a YAML file."""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            raise ValueError(f"Empty or invalid YAML file: {filepath}")
        
        return data
    
    def _load_models(self) -> ModelsConfig:
        """Load and validate models.yaml."""
        data = self._load_yaml("models.yaml")
        return ModelsConfig(**data)
    
    def _load_routing(self) -> RoutingConfig:
        """Load and validate routing.yaml."""
        data = self._load_yaml("routing.yaml")
        return RoutingConfig(**data)


# Singleton instance
_config: Config | None = None


def load_config(config_dir: Path | str = "config") -> Config:
    """
    Load configuration (singleton pattern).
    
    Args:
        config_dir: Path to configuration directory
        
    Returns:
        Loaded and validated Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_dir)
    return _config


def get_config() -> Config:
    """
    Get the current configuration instance.
    
    Returns:
        Current Config instance
        
    Raises:
        RuntimeError: If config hasn't been loaded yet
    """
    global _config
    if _config is None:
        # Lazily load default configuration directory when not loaded yet.
        # This makes `get_config()` safe to call in tests and interactive runs.
        _config = load_config()
    return _config