import json

from common.base_model import PropertyBaseModel


class ExternalBase(PropertyBaseModel):
    def to_flat_dict(self, preserve_special=False):
        data = json.loads(self.json())
        return self.flatten_dict(data, preserve_special)

    @staticmethod
    def flatten_dict(data: dict, preserve_special=False):
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result1 = ExternalBase.flatten_dict(value, preserve_special)
                for key1, value1 in result1.items():
                    result[f"{key}.{key1}"] = value1
            elif isinstance(value, list):
                result1 = ExternalBase.flatten_dict(
                    dict(enumerate(value)), preserve_special
                )
                for key1, value1 in result1.items():
                    result[f"{key}#{key1}"] = value1
            elif preserve_special:
                result[key] = value
            else:
                result[key] = str(value)
        return result
