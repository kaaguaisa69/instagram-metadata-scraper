import json
import os
from dataclasses import asdict
from typing import List

from domain.contracts import PostRepository
from domain.post import Post


class JsonPostRepository(PostRepository):
    def save_posts(self, posts: List[Post], file_path: str) -> None:

        directory = os.path.dirname(file_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        serializable_posts = [asdict(post) for post in posts]

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(serializable_posts, file, ensure_ascii=False, indent=4)