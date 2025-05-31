from typing import Dict, Any, Optional, List, Union, Callable, TypeVar, Tuple
from ..common.specifier import Specifier
import datetime

class WorkUnit:
    def __init__(self, id: str, description: str=None, readonly: bool = True, **kwargs: Any) -> None:
        self._kwargs: Dict[str, Any] = kwargs
        self.id = id
        self.description = description
        self.test_func: Optional[Callable[..., List[Dict]]] = None
        self._readonly: bool = readonly
        self._whitelist: set = {'_kwargs', 'test_func', '_readonly', 'set_test_func'}
        self.results: List[Dict] = []
        self.success: bool = False
        self.specifiers: List[Specifier] = []
        self.duration = datetime.timedelta(seconds=0)
        self._error_message: str = ''

    def add_specifiers(self, *specifiers: Specifier) -> 'WorkUnit':
        self.specifiers.extend(specifiers)
        return self

    def set_test_func(self, func: Callable[..., List[Dict]]) -> 'WorkUnit':
        self.test_func = func
        return self

    def update_kwargs(self, **kwargs: Any) -> 'WorkUnit':
        if self._readonly:
            raise TypeError("Cannot modify kwargs when object is read-only.")
        self._kwargs.update(kwargs)
        return self

    def enable_kwargs_modification(self) -> 'WorkUnit':
        self._readonly = False
        return self

    @property
    def kwargs(self) -> Dict[str, Any]:
        return self._kwargs

    def specify(self, res: Union[Dict, List[Dict]]) -> None:
        if not isinstance(res, list):
            results_list = [res]
        else:
            results_list = res
        for specifier in self.specifiers:
            specifier.validate(results_list)

    def set_result(self, results: Union[Dict, List[Dict]], success: bool = True) -> 'WorkUnit':
        self.results = results if isinstance(results, list) else [results]
        self.success = success
        self.specify(self.results)
        return self

    def reset(self) -> 'WorkUnit':
        self.results = []
        self.success = False
        self._error_message = ''
        return self

    def get_result(self) -> Tuple[List[Dict], bool]:
        return self.results, self.success

    @property
    def error_message(self) -> str:
        return self._error_message

    def run(self) -> None:
        if self.test_func is None:
            raise ValueError("No test function defined")
        try:
            starttime = datetime.datetime.now()
            self.results = self.test_func(**self.kwargs)
            endtime = datetime.datetime.now()
            self.duration = endtime-starttime
            self.success = True
        except Exception as e:
            self.success = False
            self._error_message = str(e)
        else:
            self.specify(self.results)