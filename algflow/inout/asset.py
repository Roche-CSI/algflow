#  Asset class
#   model = Asset(url='base-caller/5/1.0.0')
#


class Asset(object):
    def __init__(self, *args, **kwargs):
        path = args[0] if len(args) > 0 else kwargs.get('path', None)
        if path:
            self.path = path
            parts = path.split('/')
            self.klass = parts[0]
            self.id = parts[1] if len(parts) > 1 else None
            self.version = parts[2] if len(parts) > 2 else None
        else:
            self.klass = kwargs.get('asset_class')
            self.id = kwargs.get('asset_id', None)
            self.version = kwargs.get('version', None)

    def asset_url(self):
        return f"{self.klass}/{self.id}/{self.version}"

    def resolve(self, params):
        # format name  based on param value
        # format version based on param value
        pass


def remove_asset_from_props(props):
    variables = props['__variables__']
    for k, v in variables.items():
        if v.type == 'assset':
            del props[k]