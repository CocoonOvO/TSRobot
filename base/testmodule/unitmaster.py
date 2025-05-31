import textwrap
from typing import List
from .workunit import WorkUnit
from ..recorder import BaseRecorder
from ..common.msger import Msger
import datetime

class UnitMaster:
    def __init__(self):
        self.units:List[WorkUnit] = []
        self.recorders:List[BaseRecorder] = []
        self.runed = False
        self.starttime = datetime.datetime.now()
        self.endtime = datetime.datetime.now()
        self.duration = datetime.timedelta(seconds=0)
        self.succeed_units, self.failed_units = [],[]
    
    def add_unit(self,workunit:WorkUnit):
        self.units.append(workunit)
        return self
    
    def add_recorder(self,recorder:BaseRecorder):
        self.recorders.append(recorder)
        return self
    
    def load_units(self):
        return self.units
    
    def combine_master(self,another_master):
        [self.add_unit(unit) for unit in another_master.load_units()]
        return self
    
    def report_result(self):
        if not self.runed:
            return
        # TODO 企业微信输出可以扣了，后续看怎么解决
        # 区分成功与否放在这里不合适，交给recorder区分吧，不然报错用例不好搞
        for unit in self.succeed_units:
            for recorders in self.recorders:
                recorders.record(unit)
        msg = textwrap.dedent('''### 测试任务执行记录。本次共执行<font color="info">{total_count}</font>条用例
            > 执行开始时间: <font color="comment">{starttime}</font>
            > 执行结束时间: <font color="comment">{endtime}</font>
            > 总用时: <font color="comment">{duration}</font>
            > 执行成功用例数: <font color="info">{succeed_count}</font>
            > 执行失败用例数: <font color="warning">{fail_count}</font>
            ''').format(total_count=len(self.units),starttime=self.starttime,endtime=self.endtime,duration=self.duration,succeed_count=len(self.succeed_units),fail_count=len(self.failed_units))
        msg += '\n各任务执行统计如下: \n'
        for unit in self.units:
            if unit.success:
                td=unit.duration
                duration = str(td.seconds//3600) + "h" + str((td.seconds//60)%60) + "m" + str(td.seconds%60) + "s"
                msg += '> {name}: {state}, 耗时{duration}\n'.format(name=unit.id,state='<font color="info">成功</font>',duration='<font color="comment">'+duration+'</font>')
            else:
                msg += '> {name}: {state}, 原因: {ex}\n'.format(name=unit.id,state='<font color="warning">失败</font>',ex='<font color="comment">'+unit.error_message+'</font>')
        Msger().send_msg(msg)
        
    
    def run(self):
        self.starttime = datetime.datetime.now()
        for unit in self.units:
            unit.run()
        self.endtime = datetime.datetime.now()
        td=self.endtime-self.starttime
        self.duration = str(td.seconds//3600) + "h" + str((td.seconds//60)%60) + "m" + str(td.seconds%60) + "s"
        self.runed = True
        if td.days > 0:
            duration = str(td.days) + "d" + self.duration
        self.succeed_units = [unit for unit in self.units if unit.success]
        self.failed_units = [unit for unit in self.units if not unit.success]
        self.report_result()
        
