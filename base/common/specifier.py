from typing import Dict, Any, List, Optional, TypeVar
from base.utils.tabwing import TabWing
import dataclasses
T = TypeVar('T', bound=Dict)


@dataclasses.dataclass
class Specifier:
    name: str
    fields: Dict[str, type]
    data: List[Dict] = dataclasses.field(default_factory=list)
    specified: bool = False

    def __init__(self, name: str, fields: Dict[str, type], easy_trans: Optional[Dict[str,str]] = None):
        self.name = name
        self.fields = fields
        self.data = []
        self.easy_trans = {i:easy_trans[i] for i in easy_trans if i in fields} if easy_trans is not None else {i:i for i in fields}
        self.specified = False

    def validate(self, values: List[T]) -> bool:
        self.data = []
        for value in values:
            data_value = {}
            for name, field_type in self.fields.items():
                if not isinstance(value.get(name), field_type):
                    self.specified = False
                    return self.specified
                data_value[name] = value.get(name)
            self.data.append(data_value)
        self.specified = True
        return self.specified
    
    def get_data(self):
        return self.data
    
    def get_transdata(self):
        tabw = TabWing(self.data)
        tabw = tabw.pick(list(self.easy_trans.keys())).rename(list(self.easy_trans.keys()),list(self.easy_trans.values()))
        return tabw.write_to_dicts()