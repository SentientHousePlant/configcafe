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

        self.pretty_print()

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
