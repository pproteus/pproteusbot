import os
import inspect
import asyncio
from importlib import import_module
from base_plugin import Plugin


class Mediator:
    def __init__(self):
        self.plugins = {}
        self.initial_plugin_search = {}

        for path, _, files in os.walk("plugins"):
            for filename in files:
                if (filename.endswith('.py')  and not os.path.basename(filename).startswith('_') ):
                    newpath = path.replace(".","").lstrip("\\").replace("\\", ".") 
                    if len(newpath):
                        modulename = newpath + "." + filename[:-3]
                    else:
                        modulename = filename[:-3]
                    print(f"Loading module: {modulename}")
                    module = import_module(modulename)

                    for name, plugin in inspect.getmembers(inspect.getmodule(module), inspect.isclass):
                        if issubclass(plugin, Plugin) and plugin != Plugin:
                            self.initial_plugin_search[name] = plugin
    
    def install_one_plugin(self, plugin_class):
        if plugin_class.name in self.plugins.keys():
            return #already installed. Any new plugins need to have unique names.
        for req in plugin_class.requirements:
            self.install_one_plugin(self.initial_plugin_search[req])
        requirements = [self.plugins[req] for req in plugin_class.requirements]
        print(f"Installing plugin: {plugin_class.name}")
        self.plugins[plugin_class.name] = plugin_class(self, *requirements)
    
    def install_all_plugins(self):
        for _, plugin, in self.initial_plugin_search.items():
            self.install_one_plugin(plugin)

    async def main(self):
        async with asyncio.TaskGroup() as tg:
            for p in self.plugins.values():
                if p.needs_own_loop:
                    tg.create_task(p.loop()) 


if __name__ == "__main__":
    m = Mediator()
    m.install_all_plugins()
    asyncio.run(m.main())