from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime


@dataclass
class Image:
    image_id: str
    user_id: str
    s3_key: str
    status: str
    uploaded_at: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)
    additional_info: Dict = field(default_factory=dict)
    
    