class SettingsRepository:
    def get(self, key: str) -> str:
        return self._get(key)

    def _get(self, key: str) -> str:
        return "value"