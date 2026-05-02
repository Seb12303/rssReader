import yaml
from pathlib import Path

_config: dict | None = None


def load_config() -> dict:
    global _config
    if _config is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(
                f"config.yaml not found at {config_path}. "
                "Copy config.yaml.example to config.yaml and fill in your settings."
            )
        with open(config_path, "r") as f:
            _config = yaml.safe_load(f)
    return _config


def ai_config() -> dict:
    return load_config().get("ai", {})
