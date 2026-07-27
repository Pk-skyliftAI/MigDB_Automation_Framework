from datetime import datetime


class TestData:

    @staticmethod
    def unique_alias(prefix="AUTO_SOURCECDB"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"