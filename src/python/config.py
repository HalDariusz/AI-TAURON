from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    postgres_dsn: str = "postgresql://ai_tauron:changeme@localhost:5432/ai_tauron"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    legal_acts_collection: str = "legal_acts"
    contracts_collection: str = "contracts"

    # Ollama
    ollama_url: str = "http://localhost:11434"
    llm_model_name: str = "mistral"
    llm_temperature: float = 0.1
    llm_timeout: float = 120.0

    # Embedding
    embedding_model_name: str = "sdadas/mmlw-roberta-large"

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment: str = "ai-tauron-compliance"

    # RAG
    retrieval_top_k: int = 10
    chunk_max_tokens: int = 1024
    chunk_min_tokens: int = 128

    # Hyperledger Fabric
    hlf_enabled: bool = False
    hlf_gateway_url: str = "http://localhost:3001"
    hlf_channel: str = "compliance-channel"
    hlf_chaincode: str = "compliance-registry"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
