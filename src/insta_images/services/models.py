from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime


@dataclass
class Image:
    image_id: str
    user_id: str
    s3_key: str
    uploaded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)
    additional_info: Dict = field(default_factory=dict)
    is_live: bool = True
    is_archived: bool = False
    is_deleted: bool = False
