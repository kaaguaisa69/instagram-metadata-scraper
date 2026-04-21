from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Post:
    # Representa la metadata principal de una publicación de Instagram.
    shortcode: str
    post_id: str
    permalink: str
    date_utc: str
    caption: Optional[str]
    hashtags: List[str]
    mentions: List[str]
    typename: str
    is_video: bool
    likes: int
    comments: int
    url: str
    location: Optional[str]
    tagged_users: List[str]
    owner_username: str