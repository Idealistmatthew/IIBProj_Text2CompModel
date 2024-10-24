import json
import os

class Cache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_path(self, cache_file):
        return os.path.join(self.cache_dir, f"{cache_file}.json")

    def set(self, cache_file, value):
        cache_path = self._get_cache_path(cache_file)
        with open(cache_path, 'w') as f:
            json.dump(value, f)

    def get_cache(self, cache_file):
        cache_path = self._get_cache_path(cache_file)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_value(self, cache_file, key):
        cache = self.get_cache(cache_file)
        if cache is not None and key in cache:
            return cache[key]
        return None

    def delete_cache_file(self, cache_file):
        cache_path = self._get_cache_path(cache_file)
        if os.path.exists(cache_path):
            os.remove(cache_path)
    
    def delete_cache_entry(self, cache_file, key):
        cache = self.get_cache(cache_file)
        if cache is not None and key in cache:
            del cache[key]
            self.set(cache_file, cache)
    
    def add(self, cache_file, new_entry):
        cache_path = self._get_cache_path(cache_file)
        data = []
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Existing data is not a dict, cannot add entry.")
        data.update(new_entry)
        with open(cache_path, 'w') as f:
            json.dump(data, f)