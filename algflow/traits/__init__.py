from traits.api import *


class Asset(String):
    default_value = None
    info_text = "asset path"
    def validate(self, object, name, value):
        value = super().validate(object, name, value)
        if '/' not in value:
            self.error(object, name, value)
        else:
            return value
