from base.common.specifier import Specifier

data = {'case_name':str,'out_come':str,'duration':float}

trans = {'case_name':'用例名称','out_come':'执行结果','duration':'用例耗时'}

pytestSpecifier = Specifier(name='pytestSpecifier',fields=data,easy_trans=trans)