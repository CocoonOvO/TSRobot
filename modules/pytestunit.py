from base.testmodule.workunit import WorkUnit
from .specifiers.pytestspecifier import pytestSpecifier
import pytest

class TestResultCollecter:
    def __init__(self):
        self.reports = []

    def pytest_runtest_logreport(self, report):
        # 仅在测试执行阶段（'call'）收集报告
        if report.when == 'call':
            self.reports.append(report)

class PytestWorkUnit(WorkUnit):
    # 执行pytest用例并返回结果
    def __init__(self, id: str, filename: str, readonly: bool = True, **kwargs: any) -> None:
        super().__init__(id, readdonly=readonly, **kwargs)
        self.set_case(filename)
        self.collecter = TestResultCollecter()
        self.add_specifiers(pytestSpecifier)
        self.set_test_func(self.pytest_func)
    
    def set_case(self,filename):
        self.filename = filename
    
    def pytest_func(self,**kwargs:any):
        exit_code = pytest.main(args=['-v',self.filename], plugins=[self.collecter])
        return [{'case_come':report.nodeid,'out_come':report.outcome,'duration':report.duration} for report in self.collecter.reports]