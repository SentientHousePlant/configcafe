from typing import Type
from rich.table import Table
from rich.console import Console


class ConfigBeanMeta(type):
    def __new__(cls, name, bases, dic):

        inherits_config_info = any(
            ["_config_info" in base.__dict__ for base in bases]
        )

        if not inherits_config_info:
            config_dict = {}

            for prop in dic:
                if not (prop.startswith("__") or prop.endswith("__")):
                    config_dict[prop] = {
                        "value": dic[prop],
                        "from": dic["__qualname__"],
                    }

            dic["_config_info"] = config_dict

        if inherits_config_info:
            config_dict_from_bases = {}
            list_of_config_infos = [
                base.__dict__["_config_info"] for base in bases
            ]

            for config_info in list_of_config_infos:
                config_dict_from_bases.update(config_info)

            for prop in dic:
                if not (prop.startswith("__") or prop.endswith("__")):
                    config_dict_from_bases[prop] = {
                        "value": dic[prop],
                        "from": dic["__qualname__"],
                    }

            dic["_config_info"] = config_dict_from_bases

        return super().__new__(cls, name, bases, dic)

    def __call__(self):

        # import os

        # os_environ = os.environ

        # temp_dict = {k ,v }

        return {k: v["value"] for k, v in self._config_info.items()}

    def pretty_print(self):

        table = Table(title="Config Info", show_lines=True)

        table.add_column("Key", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta", overflow="ellipsis")
        table.add_column("From", justify="right", style="green")

        for k, v in self._config_info.items():
            config_key = str(k)
            config_value = str(v["value"])
            from_value = str(v["from"])

            table.add_row(config_key, config_value, from_value)

        console = Console()
        console.print(table)


def configbean(cls: Type):

    import os

    # Checks base classes for _config_info_, a dict containing
    # all infomation about config. attrs, and
    # adds them to a list.
    config_infos = [
        base.__dict__["_config_info_"]
        for base in cls.__bases__
        if "_config_info_" in base.__dict__
    ]

    # We compile all of these _config_info_'s into a dictionary,
    #  with overwritten values.
    settled_bases_config_info = {
        k: v for config_dict in config_infos for k, v in config_dict.items()
    }

    # We extract the values from the class and overlay
    #  the above dict with its values.
    for k, v in cls.__dict__.items():
        if not (k.startswith("__") or k.endswith("__")):
            settled_bases_config_info[k] = {
                "value": v,
                "from": cls.__qualname__,
            }

    # Grab the OS values, and give them a special from.
    os_dict = {
        k: {"value": v, "from": "os"}
        for k, v in os.environ.items()
        if k in settled_bases_config_info
    }

    # Compile the inherited _config_dict_ and the
    #  os.environs into a single dict.
    _config_info_with_os_venvs = {**settled_bases_config_info, **os_dict}

    # This is the dicitonary that will be used
    #  by classes which inherit this class
    cls._config_info_ = settled_bases_config_info

    # This is kept incase we directly use
    #  this class (brew) for config.
    cls._config_info_with_os_ = _config_info_with_os_venvs

    @classmethod
    def brew(cls):
        return {k: v["value"] for k, v in cls._config_info_with_os_.items()}

    @classmethod
    def pour(self):

        table = Table(title="Config Info", show_lines=True)

        table.add_column("Key", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta", overflow="ellipsis")
        table.add_column("From", justify="right", style="green")

        for k, v in self._config_info_with_os_.items():
            config_key = str(k)
            config_value = str(v["value"])
            from_value = str(v["from"])

            table.add_row(config_key, config_value, from_value)

        console = Console()
        console.print(table)

    cls.brew = brew

    cls.pour = pour

    return cls


if __name__ == "__main__":

    @configbean
    class Default:

        my_val = 5

    @configbean
    class Dev(Default):

        my_val_2 = 10

    Dev.brew()

    Dev.pour()
