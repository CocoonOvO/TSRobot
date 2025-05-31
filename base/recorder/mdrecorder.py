from typing import Optional

from ..common.specifier import Specifier
from .baserecorder import BaseRecorder
from ..utils.tabwing import TabWing
from ..testmodule.workunit import WorkUnit
import datetime


class MdRecorder(BaseRecorder):
    def __init__(self,path:Optional[str] = None):
        if path is not None:
            self.path = path
        else:
            # TODO 这里的reports默认路径不太合适，可以梳理下
            self.path:str = str('reports/')
        super().__init__()
    
    def record(self,workunit:WorkUnit,specifier:Optional[Specifier] = None):
        if not workunit.success:
            filename = self.path + workunit.id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'_failed.md' 
        results = specifier.get_transdata() if specifier is not None else workunit.results
        tb = TabWing(results)
        tabstr = tb.write_to_md_table()
        filename = self.path + workunit.id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.md'
        with open(filename,'w') as f:
            f.writelines(tabstr)
        return super().record(workunit)

class MdErrorRecorder(MdRecorder):
    def record(self,workunit:WorkUnit,specifier:Optional[Specifier] = None):
        if workunit.success:
            return
        emsg = workunit.error_message
        filename = self.path + workunit.id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'_error.md'
        with open(filename,'w') as f:
            f.write(emsg)
        return super().record(workunit)
