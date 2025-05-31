from typing import Optional
from .baserecorder import BaseRecorder
from ..utils.tabwing import TabWing
from ..testmodule.workunit import WorkUnit
from ..common.msger import Msger
from ..common.specifier import Specifier
import datetime

class MsgRecorder(BaseRecorder):
    def record(self, workunit: WorkUnit):
        if not workunit.success:
            return
        if len(workunit.specifiers) == 0 or not workunit.specifiers[0].specified:
            results = workunit.results
        else:
            results = workunit.specifiers[0].get_transdata()
        tb = TabWing(results)
        tabstr = tb.write_to_md_table()
        file_name = workunit.id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.md'
        Msger().send_file_from_string(filename=file_name,file_str=tabstr)
        return super().record(workunit)