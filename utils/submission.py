import uuid
from datetime import datetime

class SubmissionRecord:
    """
    Represents a logged submission for tracking.
    """

    def __init__(self, email: str, url: str):
        self.id = str(uuid.uuid4())
        self.email = email
        self.url = url
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "url": self.url,
            "timestamp": self.timestamp.isoformat() + "Z"
        }
