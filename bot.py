import os
import inspect
import asyncio
from importlib import import_module
from base_plugin import Plugin, PluginWithLoop


class Mediator:
    def __init__(self, config_folder="plugins/config", plugins_folder="plugins"):
        self.config_folder = config_folder
        self.plugins_folder = plugins_folder
        self.plugins = {}
        self.initial_plugin_search = {}

        for path, _, files in os.walk(self.plugins_folder):
            for filename in files:
                if (filename.endswith('.py') and not os.path.basename(filename).startswith('_') ):
                    newpath = path.replace(".","").lstrip("\\").replace("\\", ".") 
                    if len(newpath):
                        modulename = newpath + "." + filename[:-3]
                    else:
                        modulename = filename[:-3]
                    print(f"Loading module: {modulename}")
                    module = import_module(modulename)

                    for name, plugin in inspect.getmembers(inspect.getmodule(module), inspect.isclass):
                        if issubclass(plugin, Plugin) and plugin != Plugin and plugin != PluginWithLoop:
                            self.initial_plugin_search[name] = plugin
        if not len(self.initial_plugin_search):
            if os.path.isdir(self.plugins_folder):
                print("Warning: no plugins found in the plugin folder. You may want to put some in there!")
            else:
                print("Warning: plugin folder not found. Did you choose the path incorrectly?")

    def install_one_plugin(self, plugin_class):
        if plugin_class.name in self.plugins.keys():
            return #already installed. Any new plugins need to have unique names.
        for req in plugin_class.requirements:
            self.install_one_plugin(self.initial_plugin_search[req])
        requirements = [self.plugins[req] for req in plugin_class.requirements]
        print(f"Installing plugin: {plugin_class.name} from {plugin_class.__module__}")
        self.plugins[plugin_class.name] = plugin_class(self, *requirements)
    
    def install_all_plugins(self):
        for _, plugin, in self.initial_plugin_search.items():
            self.install_one_plugin(plugin)

    def fetch_config_filepath(self, plugin, filename):
        """Plugins really shouldn't need to go rooting around for their config files.
        Inside the main config folder will be a subfolder for each plugin."""
        filepath = os.path.join(self.config_folder, plugin.name, filename)
        dir_path = os.path.dirname(filepath)
        os.makedirs(dir_path, exist_ok=True)
        with open(filepath, 'a'): # create the file if it doesn't exist
            pass
        return filepath

    async def main(self):
        async with asyncio.TaskGroup() as tg:
            for p in self.plugins.values():
                if isinstance(p, PluginWithLoop):
                    tg.create_task(p.loop()) 


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-p", "--plugins", type=str, default="plugins", help="Plugins folder location")
    parser.add_argument("-c", "--config", type=str, default="plugins/config", help="Config folder location")
    args = parser.parse_args()

    m = Mediator(config_folder=args.config, plugins_folder=args.plugins)
    m.install_all_plugins()
    asyncio.run(m.main())
