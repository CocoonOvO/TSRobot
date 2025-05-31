# -*- coding:utf-8 -*-

import sys
from typing import Callable, Dict, List,Union

def table_to_list(fname)->List:
    '''
    将报表文件转为列表格式
    
    参数：
        fname为目标聚合报表文件名
    
    返回值：
        ls为列表，第一行为表头，其余行为各表项
    '''
    with open(fname,'r',encoding='utf-8') as f:
        ls = f.readlines()
    ls = [i.split(',') for i in ls]
    return ls

def table_to_dict(fname):
    '''
    将报表文件转为字典形式

    参数：
        fname为目标聚合报表文件名
    
    返回值：
        res为列表，其中每项为一个字典表示一个表项，键为表头
    '''
    with open(fname,'r',encoding='utf-8') as f:
        ls = f.readlines()
    keys = ls[0].split(',')
    res = [dict(zip(keys,i.split(','))) for i in ls[1:]]
    return res
    
def list_to_md_table(table_head, src_list):
    '''
    将数据列表转为md表格

    参数：
        table_head为表格表头
        src_list为数据项列表，每个数据项以列表形式存储数据

    返回值：
        一个字符串，内容为markdown中的一段表格数据。表格第一行为表头，之后各行为具体数据

    table_to_list的返回列表第一项是表头，切记
    '''
    head_str = '| {} |\n'.format(' | '.join(table_head))
    if len(src_list) <=0:
        return head_str
    subline_str = '|'+' :--- |'*len(src_list[0])+'\n'
    items_str = ['| {} |\n'.format(' | '.join([str(i) for i in item])) for item in src_list]
    return head_str+subline_str+''.join(items_str)


class TabWing(object):
    '''
    报表处理类，利用前述提取函数获得的数据，也支持直接从文件提取报表数据

    处理方式包括列选取，行过滤等
    懒得做详细介绍了慢慢看吧

    数据：
        heads: 列表类型，表示表头
        data: 列表类型，表示具体的数据行，每项以列表方式保存行数据

    功能函数：
        pick(heads)
        pickout(heads)
        filter(head fun)
    '''

    def get_from_list(self, src:List):
        '''
        从列表中读取数据。

        参数:
            src: 列表，格式应符合table_to_list的返回值格式，即列表第一行为表头列表，其余行为数据列表

        处理:
            从src中提取表头数据保存至类变量heads，提取其余数据保存至data

        TODO: 校验src是否符合格式
        '''
        self.heads = src[0]
        self.data = src[1:]

    def get_from_dict(self, src:List[Dict]):
        '''
        从字典中读取数据

        参数:
            src: 列表，格式应符合table_to_dict的返回值格式，即列表每项为一个字典，键为表头，值为对应数据

        处理:
            从src中提取表头数据保存至类变量heads，提取其余数据保存至data

        TODO: 校验src是否符合格式
        ''' 
        self.heads = list(src[0].keys())
        self.data = [list(i.values()) for i in src]

    def get_from_file(self, src:str):
        '''
        从文件中读取数据

        参数:
            src: 字符串，表示要读取的文件

        处理:
            使用table_to_list读取文件获得数据，再使用get_from_list读取数据

        TODO: 校验src是否符合格式，文件是否存在
        '''
        self.get_from_list(table_to_list(src))

    def __init__(self, src):
        '''
        构造函数，从src获取数据

        参数:
            src: 字典/列表/文件名字符串

        处理:
            根据src类型不同使用不同方式读取数据
        '''
        self.data:list = []
        self.heads:list = []
        self.none = False
        if type(src) == list:
            if len(src) == 0:
                self.heads = []
                self.results = []
                return
                self.none = True
            if type(src[0]) == list:
                self.get_from_list(src)
            elif type(src[0]) == dict:
                self.get_from_dict(src)
        elif type(src) == str:
            self.get_from_file(src)
        else:
            return None

    def pick(self, heads:List[str]):
        '''
        列选择，从数据中选择需要的列

        参数:
            heads: 数组，选择的列的表头

        返回值:
            一个TabWing对象，其heads与data为选择后的结果

        TODO: 现在的选取方式性能贼差，以后如果需要处理大量数据应该要优化
        '''
        pick_heads = heads    # 添加这个多此一举的pick_heads是为了和pickout函数统一
        heads_index = [self.heads.index(i) for i in pick_heads]
        # 突然有了个使用eval加速pick的思路。不过这一步本身速度要求不高，能不用eval还是先别用了(吐槽：是啥思路啊过了这么久全忘了)
        pick_data = [[line[i] for i in heads_index] for line in self.data]    # 二重嵌套实现选择，目测效率低到发疯
        return TabWing([heads]+pick_data)

    def pickout(self,heads):
        '''
        列排除，从数据中选择需要的列

        参数:
            heads: 数组，需要排除的列的表头

        返回值:
            一个TabWing对象，其heads与data为选择后的结果

        TODO: 现在的选取方式性能贼差，以后如果需要处理大量数据应该要优化
        TODO: 参数校验。讲道理各种校验着实难受不想搞
        '''
        pick_heads = [i for i in self.heads if i not in heads]    # 通过反选得到剩余列
        heads_index = [self.heads.index(i) for i in pick_heads]
        pick_data = [[line[i] for i in heads_index] for line in self.data]    # 同pick函数，二重嵌套实现选择效率低
        return TabWing([heads]+pick_data)

    '''
    旧的filter思路
    def filter(self,head,func):
        
        行过滤

        参数:
            head: 类型不定，用于过滤比较的表头，具体类型与表头相同
            func: 函数类型，表示比较方式(推荐使用lambda)，接受一个参数表示该项值，返回值为布尔类型

        返回值:
            一个TabWing对象，其heads与data为过滤后的结果

        TODO: 感觉这个设计还是麻烦了，不知道后面有么有改进方案（可能要从架构层面改进）
        
        head_index = self.heads.index(head)
        filter_data = [line for line in self.data if func(line[head_index])]
        return TabWing([self.heads]+filter_data)
    '''

    def filter(self,func:Callable[[dict],bool]):
        '''
        行过滤

        参数:
            func: 函数类型，表示比较方式(推荐使用lambda)，需要接受一个参数（该参数为字典类型，表示data中的一行数值，字典键为对应表头），返回值为布尔类型

        过程:
            遍历data中的所有行，分别将行数据作为参数调用filter，保留返回值为True的行

        返回值:
            一个TabWing对象，其heads与data为过滤后的结果
        
        '''
        dict_data = dict(zip(self.heads,self.data))
        filter_data = [line for line in list(dict_data.values()) if func(line)]  # wdnmd这速度慢的要死这是碳基生物能写出来的？
        return TabWing([self.heads]+filter_data)

    @staticmethod
    def contact(wings:List['TabWing']):
        '''
        类函数，左右合并多个TabWing

        参数:
            wings:  列表，表示要合并的TabWing，每项为一个TabWing对象
        返回值:
            一个TabWing对象，为合并后的结果
        TODO: 迟早需要找一个二重循环嵌套的代替方案
        '''
        contact_heads = []
        [contact_heads.extend(wing.heads) for wing in wings]    # 连接所有wings的head元素，注意extend函数本身并不返回值
        contact_data = wings[0].data
        [[contact_data[i].extend(wing.data[i]) for wing in wings[1:]] for i in range(len(contact_data))]
        return TabWing([contact_heads]+contact_data)

    def rename(self,heads:Union[str,List[str]],new_heads:Union[str,List[str]]):
        '''
        重命名heads

        输入:
            heads: 需要重命名的表头，可以单个，也可以多个，多个需要为列表类型
            new_heads: 重命名后的表头，多个需要为列表类型

        返回值:
            修改本对象heads后返回self
        '''
        if(type(heads)==list):
            [self.rename(heads[i],new_heads[i]) for i in range(len(heads))]
        else:
            self.heads[self.heads.index(heads)] = new_heads
        return self

    def write_to_dicts(self):
        '''
        以字典格式输出结果

        处理：逐行处理data，以heads为键转为字典并最终变成字典列表
        
        返回值:
        一个列表，每项为一个字典，对应data中的一条数据，键是heads
        '''
        return [{self.heads[i]:data[i] for i in range(len(data))} for data in self.data]

    def write_to_md_table(self):
        '''
        输出为markdown的table表格字符串

        处理：调用list_to_md_table

        返回值：
        一个字符串，内容为markdown中的一段表格数据。表格第一行为表头，之后各行为具体数据
        '''
        return list_to_md_table(self.heads,self.data)
