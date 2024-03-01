from ampapi.apimodules.ADSModule import IADSInstance, Instance

class AmpInstanceMap:
    def __init__(self):
        self.instance_map = {}
        self.server_map = {}

    def add_instance(self, instance : Instance):
        name = instance.FriendlyName.lower().replace(' ','')
        self.instance_map[name] = instance.InstanceID
        self.server_map[name] = instance

    def get_instance(self, name : str) -> int:
        return self.instance_map.get(name)

    def get_server(self, name : str) -> Instance:
        return self.server_map.get(name)

class ADSInstanceData:
    def __init__(self, Data : IADSInstance):
        self.installed_ram = Data.Platform.InstalledRAMMB
        self.used_ram = 0
        self.instances = Data.AvailableInstances
        self.server_map = AmpInstanceMap()
        for instance in self.instances:
            self.server_map.add_instance(instance)
            if instance.Metrics:
                self.used_ram += instance.Metrics["Memory Usage"].RawValue
    
    def __len__(self):
        return len(self.instances)

    def iterate_instances(self):
        for instance in self.instances:
            yield instance

    def get_instance(self, name : str) -> int:
        return self.server_map.get_instance(name)
    
    def get_server(self, name : str) -> Instance:
        return self.server_map.get_server(name)