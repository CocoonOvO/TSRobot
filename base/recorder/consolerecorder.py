from .baserecorder import BaseRecorder
from ..utils.tabwing import TabWing
from ..testmodule.workunit import WorkUnit


class ConsoleRecorder(BaseRecorder):
    def record(self, workunit:WorkUnit):
        if workunit.success:
            results = workunit.results
            tb = TabWing(results)
            print('#用例名: ', workunit.id)
            print('\t'.join(tb.heads))
            for line in tb.data:
                print('\t'.join([str(item) for item in line]))
        else:
            print('用例失败: ', workunit.id)
            print('错误信息: ', workunit.error_message if hasattr(workunit, 'error_message') else '未知错误')
        return super().record(workunit)