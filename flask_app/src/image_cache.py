class ImageCache():
    id = 0
    cache: list[str] = []

    def clear_cache(self):
        self.id = 0
        self.cache = []

    def add_to_cache(self, data: str) -> int:
        self.cache.append(data)
        self.id += 1
        return self.id - 1
    
    def get_from_cache(self, id: int) -> str:
        return self.cache[id]


image_cache = ImageCache()