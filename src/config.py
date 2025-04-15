import yaml
import os

class Config:
    def __init__(self, config_path="config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, *keys, default=None):
        """Access config with dot-like syntax, e.g., get('model', 'path')"""
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value or default

# Ejemplo de uso
if __name__ == "__main__":
    cfg = Config()
    print(cfg.get("model", "path"))
    print(cfg.get("sensors", "read_interval"))