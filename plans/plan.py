import dataclasses
import os
import yaml

@dataclasses.dataclass
class Plan:
    # plan的标准结构。
    # id命名方式不做限制，保证唯一即可
    id: str  # 计划ID/名称
    description: str = dataclasses.field(default=None)  # 计划描述，默认为None
    cases: list = dataclasses.field(default_factory=list)  # 计划用例列表，默认为空列表
    recorders: list = dataclasses.field(default_factory=list)  # 记录者列表，默认为空列表
    unique: bool = dataclasses.field(default=False)  # 用例是否去重，默认为False
    combined_plans: list = dataclasses.field(default_factory=list)  # 合并其他计划（用于组件大批量运行计划）,统一使用当前计划的recorder，默认为空列表

def get_plan_from_yaml(yaml_file):
    # 从yaml文件中读取plan信息
    with open(yaml_file, 'r', encoding='utf-8') as f:
        plan_dict = yaml.load(f, Loader=yaml.FullLoader)
    # 每个yaml中可能以列表形式存储多个plan，需要全部读取成为Plan列表
    plans = []
    if isinstance(plan_dict, list):
        for p in plan_dict:
            plans.append(Plan(**p))
    else:
        plans.append(Plan(**plan_dict))
    return plans

def get_all_plans(dirname: str):
    # 获取指定目录下的所有yaml文件，并读取plan信息
    plans = []
    for file in os.listdir(dirname):
        if file.endswith('.yaml'):
            plan_file = os.path.join(dirname, file)
            plans.extend(get_plan_from_yaml(plan_file))
    return plans

if __name__ == '__main__':
    # 测试用例
    plans = get_plan_from_yaml('c:\code\TSRobot\plans\\testplan.yaml')
    for plan in plans:
        print(plan)