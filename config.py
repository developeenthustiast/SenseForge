"""
SenseForge Configuration Management
Centralized configuration with environment variable support and validation.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

load_dotenv()

class APIConfig(BaseModel):
    """API configuration settings"""
    cambrian_api_key: Optional[str] = Field(default=None, env="CAMBRIAN_API_KEY")
    cambrian_base_url: str = Field(default="https://opabinia.cambrian.org")
    letta_api_key: Optional[str] = Field(default=None, env="LETTA_API_KEY")
    letta_base_url: str = Field(default="https://api.letta.com")
    ambient_api_key: Optional[str] = Field(default=None, env="AMBIENT_API_KEY")
    
class AgentConfig(BaseModel):
    """Agent runtime configuration"""
    agent_id: str = Field(default="senseforge-risk-oracle-001")
    mode: str = Field(default="mock")  # "mock" or "live"
    enable_training: bool = Field(default=True)
    training_interval_seconds: int = Field(default=300)  # Train every 5 minutes
    
    @validator('mode')
    def validate_mode(cls, v):
        if v not in ['mock', 'live']:
            raise ValueError('mode must be "mock" or "live"')
        return v

class ModelConfig(BaseModel):
    """JEPA model configuration"""
    state_dim: int = Field(default=3)
    action_dim: int = Field(default=1)
    latent_dim: int = Field(default=16)
    batch_size: int = Field(default=32)
    num_batches: int = Field(default=10)
    checkpoint_path: str = Field(default="checkpoints/jepa_model.pth")

class DashboardConfig(BaseModel):
    """Dashboard display configuration"""
    refresh_interval_seconds: int = Field(default=5)
    max_events_display: int = Field(default=50)
    chart_height: int = Field(default=400)
    enable_debug: bool = Field(default=False)

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: Optional[str] = Field(default="logs/senseforge.log")
    max_bytes: int = Field(default=10485760)  # 10MB
    backup_count: int = Field(default=5)

class Config(BaseModel):
    """Master configuration object"""
    api: APIConfig = Field(default_factory=APIConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    class Config:
        env_prefix = "SENSEFORGE_"

def load_config() -> Config:
    """Load configuration from environment variables"""
    config = Config(
        api=APIConfig(
            cambrian_api_key=os.getenv("CAMBRIAN_API_KEY"),
            letta_api_key=os.getenv("LETTA_API_KEY"),
            ambient_api_key=os.getenv("AMBIENT_API_KEY")
        ),
        agent=AgentConfig(
            mode=os.getenv("SENSEFORGE_MODE", "mock")
        )
    )
    return config

# Global config instance
config = load_config()
