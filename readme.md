# TSRobot 一个通用测试计划管理系统

## 介绍

TSRobot 是一套高扩展，高兼容性的测试计划管理方案，用于进行多测试用例场景的批量管理，组合与调用。该项目仅包含管理调用功能，理论上可以通过简单编写适配任意测试系统。该项目特点如下：

1. 兼容多种测试系统。通过自定义类可以对接其他任意系统接口，同时该项目的测试结果记录功能支持自定义测试用例结果的结构。已自带对pytest的支持

2. 易扩展。出对接其他测试系统外，该项目的结果记录方式也支持扩展，从而适配更多实际需求

3. 自由组合测试用例。通过yaml文件进行简单撰写即可自定义测试计划，自由组合计划需要的测试用例和结果记录方式

4. 提供交互式调用与命令行调用两种方式

## 使用

### 测试用例编写

测试用例类来自base.testmodule.workunit.WorkUnit

```python
class WorkUnit:
    def __init__(self, id: str, description: str=None, readonly: bool = True, **kwargs: Any) -> None
```

其参数如下：

1. id 用例名（需要保证唯一）

2. description 用例描述

3. readonly 暂时无用

4. kwargs 传给该用例的测试函数使用的参数书，在测试函数需要接受参数时可用

对于WorkUnit的继承可以放在modules/下，而具体的测试用例的实现需要放在testsuites/下，其中每个保存用例的python文件需要包含一个units列表，内容包括所有可读取的用例。项目会自动从中读取用例

WorkUnit类有以下三个关键函数用于定义测试用例

```python
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
```

其中，add_specifiers的作用是声明测试用例运行后生成的结果的结构，用于定义测试结果的结构从而便于自动生成和写入数据库表，后续详细说明；test_func作用是设置具体的测试时调用的测试函数；update_kwargs用于动态设置提供给测试函数的参数

在编写测试用例时，可以直接实现workunit类，声明用例id与描述并定义测试函数和测试结果结构，也可以根据需要继承WorkUnit生成自己的用例类，自定义的用例类建议放在modules下。

该项目中已经自带了一个针对pytest的用例类，通过传递pytest用例文件即可生成对应用例

```python
class PytestWorkUnit(WorkUnit):
    # 执行pytest用例并返回结果
    def __init__(self, id: str, filename: str, readonly: bool = True, **kwargs: any) -> None:
```

具体的测试用例生成放在testsuites下，每个文件中自由生成测试用例（注意保证测试用例id的唯一性），将所有可被读取的用例放在units数组中即可，项目会自动读取。示例如下：

```python
from modules.pytestunit import PytestWorkUnit

units = [PytestWorkUnit("test0", "test/pytestcase.py", description="测试Pytest用例")]
```

值得说明的是，在你为你的测试用例添加的test_func中，test_func的返回值应当为一个字典或一组字典列表(其中每个字典代表一套具体小用例)，字典使用键值对的形式表示你需要记录的测试用例运行内容，可能包括名称，时间，通过结果等等，字典键值需要与specifier匹配。 而对于测试用例执行时遇到的意外报错情况(非用例未通过)，只需要报错即可，报错的用例在运行时会被项目捕获

#### Specifiers编写

Specifier的本质是一组表头，用于定义测试结果的表结构，如：用例名，耗时，成功情况等，暂时仅仅用于结构化数据库记录结果。specifier不会影响测试用例的执行，只会在需要将结果记录进数据库时从测试结果中选择匹配的键值对并检验结构是否符合需要，并将匹配的结果计入数据库。

值得一提的是，在测试结果记录到数据库的过程中，是以specifier.name生成数据库表的，因此你可以让多个测试用例使用相同的specifier，也可以为一个测试用例添加多个specifier，从而按需分别记录进不同表

```python
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
            return
        results = specifier.get_transdata() if specifier is not None else workunit.results
        tb = TabWing(results)
        tabstr = tb.write_to_md_table()
        filename = self.path + workunit.id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.md'
        with open(filename,'w') as f:
            f.writelines(tabstr)
        return super().record(workunit)
```

specifier定义在base.common.specifier.Specifier中，当你需要声明自己的specifier时，只需要将其实现，并传递如下参数:

- name 字符串，表示该specifier名，需要唯一

- fields 字典，其键为列名，值为type类型，也就是该列对应的数据结构。在测试结果入库时会使用该列名作为列名，因此请注意命名

- easy_trans 字典，可选项，表示列名的翻译。键为列明，值为对应的别称。该参数主要用于将结果写入命令行，文件等只管记录方式时增加列名的可读性

specifier的实现推荐放在modules/specifiers中，其中已有一个对pytest场景的specifier实现用于参考

```python
from base.common.specifier import Specifier

data = {'case_name':str,'out_come':str,'duration':float}

trans = {'case_name':'用例名称','out_come':'执行结果','duration':'用例耗时'}

pytestSpecifier = Specifier(name='pytestSpecifier',fields=data,easy_trans=trans)
```

### 测试计划编写

测试计划能够将测试用例组合在一起，并指定结果的记录方式，该项目以yaml文件的格式编写测试计划。测试计划的编写应当放在plans/下，与测试用例类似，项目会自动读取该目录下所有yaml文件并从中取得测试计划。

plans/plan.py中定义了测试计划的格式：

```python
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


```

其中，id为计划名称，是必须项（需要保证唯一）；cases数组指定了该计划包含哪些测试用例；recorders数组指定了该计划的结果记录方式有哪些（后续详细说明）；unique标识该计划中的用例是否需要去重（即重复出现的用例只执行一次）；combined_plans数组每项为一个测试计划的id，项目会自动将其中包含的测试计划的测试用例也合并到该测试计划中，利用该参数可以便于对包含大量用例的复杂测试场景的组织

测试计划编写需要符合yaml格式，一个yaml文件中也可以以列表的方式包含多个测试计划。示例如下：

```yaml
- id: testplan.测试计划1
  description: 这是测试计划，纯控制台输出
  cases:
    - test
  recorders:
    - console
- id: testplan.测试计划2
  description: 这是测试计划，包含文件输出
  cases:
    - test
    - test
  recorders:
    - console
    - md
```

### 结果记录方式编写和扩展

该项目支持多种结果记录方式，同样支持自定义和扩展记录方式

#### 自定义已有记录方式

已实现的记录方式放在recorders/下。实现的具体记录方式需要在recorders/下的init文件中注册并声明id

```python
from .normalrecorders import console_recorder, md_recorder

recorders = {'console':console_recorder,'md':md_recorder}
```

默认支持的结果记录方式如下：

- 命令行直接输出，id为'console'

- 以表格形式写入md文件(默认生成在reports路径下), id为'md'

```python
from base.recorder.consolerecorder import ConsoleRecorder
from base.recorder.mdrecorder import MdRecorder

console_recorder = ConsoleRecorder()
md_recorder = MdRecorder(path='reports/')
```

如果需要自定义recorder，可以实现已有recorder并放在recorders下，然后在init文件中进行注册。已有Recorder类在base/recorder中，可以阅读其具体构造要求。例如，MysqlRecorder就可以通过声明数据库连接来实现，他会在指定数据库下自行根据用例是specifier选择和生成结果表

```python
class MysqlRecorder(BaseRecorder):
    def __init__(self,host:str,port:int,database:str,user:str,passwd:str):
```

#### 扩展记录方式

如果需要自定义Recorder类来扩展记录方式,可以继承base.recorders.baserecorder.BaseRecorder。根据需要定义构造函数，并实现record(self,workunit:Workunit)函数即可

```python
class BaseRecorder:
    def __init__(self):
        pass

    def record(self,workunit:WorkUnit):
        pass
```

### 测试用例执行

现阶段支持两种执行方式：交互式执行和命令行执行

#### 交互式执行

在根目录下直接运行TSRobot.py文件会进入交互式界面。根据引导选择执行具体用例或测试计划即可

```shell
 _____  ____   ____          _             _   
|_   _|/ ___| |  _ \   ___  | |__    ___  | |_ 
  | |  \___ \ | |_) | / _ \ | '_ \  / _ \ | __|
  | |   ___) ||  _ < | (_) || |_) || (_) || |_ 
  |_|  |____/ |_| \_\ \___/ |_.__/  \___/  \__|


请选择一个选项:
1. 测试用例
2. 测试计划
3. 离开
输入选项编号 [1/2/3]:
```

（注意，现阶段单独执行测试用例默认将结果输出到命令行）

#### 命令行执行

在根目录下运行TSRobot.py时，可以通过命令行参数选择要执行的用例以及计划，从而绕过交互式界面直接执行。具体参数可以使用-h参数进行查看

```shell
PS C:\code\TSRobot> python TSRobot.py -h
usage: TSRobot.py [-h] [-d] [-c CASENAME] [-p PLANNAME] [-r RECORDERS [RECORDERS ...]]

性能用例自动化执行

options:
  -h, --help            show this help message and exit
  -d, --debug           进入debug模式
  -c CASENAME, --casename CASENAME
                        执行特定单个测试用例
  -p PLANNAME, --planname PLANNAME
                        执行特定测试计划
  -r RECORDERS [RECORDERS ...], --recorders RECORDERS [RECORDERS ...]
                        指定结果记录器
```

其中，-c参数与-p参数只会有一个生效，添加这些参数只不启动交互界面直接执行对于用例/计划。 -r参数可以额外指定一批recorders用于结果记录，一般用于辅助不能直接设定的测试用例，单独声明该参数也可以在交互界面使用时生效

## 项目结构

- TSRobot  根目录
  
  - base  存放项目核心代码
    
    - common  存放通用支持类
      
      - config.py 配置文件类，暂时废弃
      
      - msger.py 通信功能，用于实现企业微信机器人等对外信息发送
    
    - recorder 存放结果记录器类
      
      - ...
    
    - testmodule 存放测试用例相关基类
      
      - workunit 测试用例基类
      
      - unitmaster 实现将多个测试用例组合在一起
    
    - utils 其他工具类
      
      - tabw 将列表/字典数据表格化并进行简单编辑的工具
  
  - conf 存放配置文件，当前项目中暂时用不到
  
  - modules 存放测试相关的继承与实现，该目录下直接存放继承自WorkUnit的测试用例类
    
    - recorders 存放实现的recorder
    
    - specifiers 存放实现的specifier，一边会被modules下的workunit子类引用
  
  - testsuites 存放具体测试用例文件
  
  - plans 存放具体测试计划文件
    
    - plan.py 定义测试计划文件的基本结构
  
  - reports 可用于测试用例执行结果写入文件输出时的保存目录

## TODDO
- 重新完善定时器功能，运行进行定时执行，定期循环执行任务