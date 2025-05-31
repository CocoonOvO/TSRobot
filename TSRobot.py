# 性能自动化用例控制，调度，循环执行
# 目标
# 1. 用于管理性能自动化用例
# 2. 在持续运行过程中，能自动判区分工作日和休息日，从而控制在空闲时间自动安排用例执行
# 3. 用例精确到bullet这个类进行区分，但具体怎么设计还没想好
# 4. 通过外部文件存储用例和执行顺序，并且支持手动热修改(这要求每次执行用例前都重新加载配置文件读取顺序)
# 5. 需要能够自动预估用例执行时间，并根据甚于可用时间安排合适的用例去执行(需要一个方案用来存储用例的上一次执行时间用于预估)
# 6. 更进一步的，可以考虑存储运行状态信息等
# 设计上
# 1. 一个进程理论上只要对应一种shoter就行，调度该shoter适配的bullet
# 2. 通过内部定时调度的方式控制运行时间，比如每天晚上九点进行判断，如果是工作日则运行到第二天早上八点，否则运行到下一个工作日早上九点，非运行时进入挂起状态
# 3. 对于工作日的判断可以通过第三方库进行
# 4. 为了方便手动热修，执行顺序可能会考虑配置文件的方式
# 5. 用例的存储以及用例预估时间的存储可以使用文件，也可以使用数据库，具体怎么方便怎么来。数据库的话可以考虑sqllite
# 6. 调度任务并执行主要在两个时间点。一个是工作日晚九点，另一个是一个任务执行完毕时。
# 7. 调度判断策略 若时间已经是工作日白天则停止执行并休眠等待下次唤醒。否则取待执行任务队列中的下一个任务，获取预估时间，如果剩余时间大于预估时间就执行，否则该任务优先级后移，取下一个任务继续判断
# 8. TODO 但上述策略有个问题，万一时间一直不够咋办，需要一个停止策略。最简单的是硬判断，离结束时间不到半小时的话就判定停止
# 9. 这样的话整个结构就很清晰了，定时器负责判断可以跑自动化的时间并唤醒程序，唤醒后执行器连接工程准备对应的shoter。调度器选取待执行的用例并交由调度器执行。每当用例执行完成后，更新预期运行时间和待执行队列(待执行队列其实任务开始后直接更新更合适)，先判断是否到了结束时间，如果没有到则选取下一个合适的用例继续进行执行
# 10. 依赖类的话主要把robotstore导入进来。其他功能按需添加即可
# 11. 需要一个策略可以显示队列的执行情况，执行了多少还差多少什么的
# 12. 这么看都有必要考虑是否该加个gui了
# 13. 需要重新审视下任务运行失败的判断逻辑和数据结构，在调度的时候需要保证能准确判断任务是正常结束还是意外中断。这主要起两个作用，一是方式意外中断的任务运行时间过短而污染预期时间，二是能够捕获那些运行失败的任务，发起提醒，并进行重跑
# 14. 多提供一个提醒模块。能够借助企业微信机器人等方式及时地反馈运行信息。主要包括：执行失败的用例，每次执行完成进入休眠时报告已执行的用例。更进一步，可以以维护一个服务器把每次的运行都转为报告(可以借助mkdocs来实现，不过这是将来的事了)
# 模块要点方面
# 1. 通用的日志模块想不到啥特别的
# 2. 定时器需要能够区分工作日和非工作日，并有在工作日晚九点唤醒的功能，唤醒时需要计算停止时间(下一个工作日早九点)，以供耗时判断
# 3. 由2可以得出，定时器只需要使用单次定时器。每次结束后定时到下次开始执行就行
# 3. 执行器主要负责任务执行就好，暂时不确定是否要在任务进行时加其他的工作。每次被调用时都最好登录一下吧(其实没必要，shoter应该有完善的登录判断功能了)
# 4. 调度器维护至少一个外部文件(或数据库？)，主要存储：各个用例信息，用例的预期运行时间，待执行用例队列。每次调度时从队列中取一个用例，判断预期时间是否足够，足够则允许， 否则降低该任务优先级并取下一个继续判断(从队首依次查看并判断时间，遇到合适的后pop出来，这个方式应该更合适些)。值得注意的时，每次调度的时候都需要重新读取队列和预期时间，这部分是不缓存的
# 4. 消息模块。与日志略有不同，模块本身提供一个发信接口。有了这个模块后其他模块为了发送需要的信息也都有不少要做的，包括但不限于记录更多信息
# 没了，就这几个模块，这么一看还挺清晰的。不过几个模块的实现方式选型还是要考虑下的
# 这套逻辑还面临着一个重要问题：不同数据库的场景不能混合。
# 由于内存原因多个数据库不能同时启动，所以测某些库的时候经常需要关掉其他库再把它起来。如果把所有场景混一起，那使用那些未启动的库的场景就会出问题
# 暂时能想到的方案，是做多个待执行队列，根据启动的库进行区分。需要测其他库了就切一下场景
# 不过具体结构还得好好规划一下。毕竟好歹是个需要持续运行和维护的程序
# Threading的定时器是异步的，每次传入执行的函数。一方面因为是异步主线程需要换个方式阻塞掉，另一方面如果要实现多次调用，每次调用内设定下一次定时器，嘶好像也不一定会导致栈持续增长
# 但不管怎样。由于主体的运行是要同步的(哪怕将来做了异步，那也大概率不需要在这一层实现)，依赖异步方案确实怪怪的。
# 对于执行时的场景，理想状态是：一个任务执行完成后，获取剩余时间，然后判断是否应该结束。如果结果为是，则发出结束指令。此时定时器在结束的计算下一次运行时间并定时
# 这个定时最搞的其实也可以用sleep，一个sleep过去（其实超长的sleep还挺担心能不能正常唤醒的）
# 或者其实可以利用下异步方式。把每次要运行的部分独立出来，相当于每次指定的时候单独生成一个运行对象之类的。
# 同时，主线程保留，一来用于定时功能，二来也起到个监控的作用
# 主线程和执行线程之间进行通信。主线程维护一个状态机，当开始执行任务时进入运行中状态，当任务结束时进入待执行状态，且进入待执行状态时计算并创建下一个定时器。空余时间主线程的无限循环也可以用来做些其他的监控功能，很随意
# 如此一来，主线程和执行线程就能区分出来，整个程序的运行流程也变得清晰
# ：从运行角度看，整个程序会分为三个部分：用于调度和监控的主线程，执行任务的执行模块，以及外部存储系统
# 从表现力上，还是有必要配上企业微信机器人。起码更能看出自己干了啥。顺便不仅要有推送，还要有总结，总结一段时间内干了什么，还是需要有表现力，不然年前那啥都不知道该干啥
# 整体上看，定时器除了设置定时任务，还需要监控运行状态。
# 定时器运行流程：
# 1. 启动，状态为预备
# 2. 计算下次开始时间与结束时间，设定定时任务并传参，状态切换为待运行，记录运行时间
# 3. 定时任务开始时将定时器状态切换为运行中
# 4. 定时任务结束时将定时器状态切换为预备。回到2
# 5. 在运行时间范围内，定时器需要检查，如果不是运行中状态，就检查是否已经有任务在运行，有则切换状态，无则立刻发起任务
# 6. 同样，待运行状态也需要检查是否有待运行的任务，没有就创建
# 7. 运行中状态需要检查是否任务已经退出，如果是则改为待运行状态
# 执行单元运行流程：
# 1. 启动时会获取运行停止时间，调用定时器切换状态
# 2. 每当要拉起一个任务，先运算当前时间与停止时间的差，得到可用时间，可用时间小于半小时则任务结束并调用定时器切换状态。然后读取待执行队列
# 3. 从任务队列顶开始读取任务，如果任务没有预期时间，则直接运行。如果有预期时间则判断预期时间是否小于可用时间，小于则运行，否则读取下一个。 确认要运行的任务需要出队
# 4. 每个任务运行完成时，把运行时间和用例名(如何取到是个问题，实在不行就不记录用例名了)传入消息模块。然后回到2
# 5. 当任务结束时，还需要额外往消息模块传一条结束消息
# 消息模块结构(仔细想想几乎就是个监听器了，可以按需优化)：
# 1. 维护一个消息队列，所有消息需要有分类
# 2. 维护一个企业微信机器人的通知方式(也通过外部文件配置吧)
# 3. 对于某些特殊类型的消息，需要进行专门处理。
# 4. 对于定时任务停止消息，会选出所有时间在消息时间范围内的定时任务运行消息，整理，发消息
# 预估下时间吧
# 1. 通用配置文件功能，选项+可行性分析+实现预计半天到一天。可行性分析挺重要的，毕竟其他模块都要用到，用的方式还不一样
# 2. 定时器，状态机需要设计一下，时间算法也得考虑下，再算上开发，差不多一天吧
# 3. 执行单元，重点在用例存储和待执行队列，在通用配置文件部分解决后这部分应该也挺简单的。除此之外还需要一两小时研究一下任务的正常结束和异常结束问题。后续的开发流程大概半天吧
# 5. 重新审视运行异常处理部分，这块得半天吧
# 4. 消息模块，主要需要思考下消息的存储结构，开发加上适配大概一天吧
# 对了，为了适配新的功能。etlshoter也得修改，放到src里，同时shoter的配置在testsuites里用配置文件保存
# 存储方式需要经过抽象，后期量大的话可能会考虑改用数据库存储(要用数据库的话mongo可能是比较好的选择，但数据库的主要问题是不方便编辑)。不过想了想，用数据库的话，无论是结构还是逻辑都和配置文件有明显区别，还算不抽象了
# 存储方式使用yaml吧，真的好用
# 关于需要外部存储的结构：
# 1. 记录用例,预估时间、
# 2. 记录shoter配置
# 3. 待运行队列
# 关于shoter的配置
# shoter这块主要有三部分信息: 工程url和登录信息(配置化很方便)，robot配置(不好配置化，但比较固定没啥问题)，配置记录方式等的shoter插件(不好配置化，也不那么固定)
# 所以shoater的配置化最大的问题是无法全部配置化，能配置化的只有工程url和登录信息
# robotstore在设计上是在初始化的时候就把各个shoter加载好。其实退一万步讲，完全可以直接由caseloader从testsuites下的robotstore里读取shoter。嗯暂时可以这么搞，后续考虑改进
# 关于用例配置：
# 需要配置的包括：以任务做区分，每个任务是一个字典，里面再列举各个子任务。任务需要记录任务id，子任务需要记录子任务id，每个任务/子任务都要有一个名称用于区分。且名称这块必须保证唯一性
# 对于任务/子任务，需要一个预期时间的字段。但预期时间写到这里就会出现个问题：如果再运行过程中手动修改配置文件会不会出问题。
#  要计算预期时间，就要求每次任务运行完后再写一次配置。依赖yaml的话这个写配置的过程就会是全量写，必然会修改文件内容
#  或者严格一点。每次运行开始时读取一次。直到所有运行结束后再写会文件。彻底阻断运行时修改的可能。不过这样和上一种其实也没本质区别
#  只能说，开始运行后就不允许修改了(那这还算哪门子热修。虽说本来也是打算让这玩意在非工作时间运行的)
# 对于任务队列。就是一个队列，存储执行任务的顺序。只不过在读取后是需要以类似循环方式使用的.
#  任务是队列存储的每个用例需要包含最多两部分，任务标识和子任务标识，分别对应的是工程中的任务id和节点id。没有子任务标识的话就认为是执行整个任务，这样比较合适
# 配置好像就这些了，再就是写运行时的策略问题了
# 然后是消息模块的设计
#  原想的是提供一个任意写入消息的功能。再提供对应的处理函数，把一批消息取出来处理掉。不过潜在的问题是可能会产生处理不掉的消息
#  实际上为了复用考虑，消息模块直接并入任务模块也不合适。
#  单个消息应当是字典形式，不做过多要求，甚至没有多少必须字段，最主要的是一个用于分类的字段做标识
#  提供消息获取和删除等功能，消息需要指定类型，同时支持函数进行过滤
#  消息发送的功能肯定是消息模块做的。问题是消息处理，生成待发送消息这里哪里来做。可以是消息模块，也可以是使用消息的模块
#  交给消息模块吧。在消息模块里可以认真定义一段消息的内容，而且万一用到的消息要跨模块，在这里定义的也最适合来干跨模块的工作
# 最后是定时器模块
#  一个基础的是时间判断算法
#  定时器本质是状态机。预备状态，待运行状态，运行中状态，现阶段应该是这三个状态之间切换
# 这么一来就很清晰了。另外未雨绸缪把日志部分也处理一下吧
# 任务运行时的日志的robot定义的不用管(将来需要想办法统一)，关键是这里的日志。info以上场景包括
# 1. 定时器模块，在状态切换和周期循环的时候进行记录切换情况
# 2. 每当生成下次运行时间的时候记录下次运行时间
# 3. 运行模块，在开始运行时记录运行时间，结束时间
# 4. 每个任务运行时都输出运行的任务，预计运行时间
# 5. 所有运行结束后再次进行记录，输出起止时间
# 6. 消息模块，整理发送的时候把消息记录一下
# debug消息随意
# 另外这次日志改用logger模块处理
# 贴一下偷来的logging格式化参数方便后面用
#  %(levelno)s: 打印日志级别的数值
#  %(levelname)s: 打印日志级别名称
#  %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
#  %(filename)s: 打印当前执行程序名，python如：login.py
#  %(funcName)s: 打印日志的当前函数
#  %(lineno)d: 打印日志的当前行号,在第几行打印的日志
#  %(asctime)s: 打印日志的时间
#  %(thread)d: 打印线程ID
#  %(threadName)s: 打印线程名称
#  %(process)d: 打印进程ID
#  %(message)s: 打印日志信息
# 宏观地重新审视下任务配置吧
# 两大部分：一是各用例信息，二是用例运行列表
# 用例信息相对好说。根据服务器场景区分不同配置文件，分别保存用例信息，预期时间等。这里比较应该注意的是，每个用例都需要一个别名之类的东西作为标识，在配置运行列表的时候，使用别名配置自然要方便的多
# 对于运行队列，本质上就是多个列表，列表内每项是用例别名。不同列表代表不同的运行，caseloader运行时需要指定运行队列
# 设置不同运行队列，主要是为了照顾那些互斥的用例（最简单的比如不能同时开启的数据库，需要手动开启才能执行其他用例。），在手动切换后可以手动切换运行队列进行适配
# 这样的似乎也没啥，主要问题是又多了一个参数用于指定运行队列，这个参数从哪来，怎么传进去
# 第一种办法是写死在代码里，太丑陋了放弃
# 第二种方式是作为外部参数，在运行时传进来
# 第三种方式是写进配置文件，看似合理实则确实可行，还能做到动态切换
# 外部参数似乎是比较正常的了。不过啊啊还是有点丑陋，不想多写参数
# 那还是第三种吧。而且第三种暂时可以不需要外部参数模块，相对简单些。而且第三种也支持队列的热切换，理论上这玩意运行起来后除了脚本更新几乎不需要再启停，光改配置就行
# 问题来了，robot和shoter由于还需要保持根据robot切换的特性，不能用配置文件的方式，必须以某种形式作为启动参数来传递
# 啊啊头疼，暂时不管了，用固定名称吧，后面遇到迁移问题再切换
# 这个东西现在面临的最大的一个问题是，抛弃了自由度。也就是单纯的只支持任务调用，其他场景呢？接口测试呢？都搞不了
# 原本把测试用例以代码形式放在testsuites下的目的是，每个场景用例可以自由开发和实现，这里的caseloader是为了切割任务和统一调度来做的
# 在定时任务的调度方面，caseloader已经趋于完善，但这玩意在最初就忘了一件事———拓展性。为了满足长久的调用运行需要，必须要把用例的概念抽象出来，不只是一个etl节点，也可以是一个接口，一批流程，一段管道运行
# 不过这样做，势必需要每个用例都单独考虑场景，用例列表文件也会更复杂
# 同时抽象出来的用例必须满足的接口包括：可执行，可获得成功与否，结果可记录（好像都还挺简单的）
# 嘶这么想想可行性还是有的
# 既要考虑复用性，又要考虑自由度，着实很艹
# 这部分抽象问题解决前，如果有其他特异用例，专门写出来放testsuites里吧，也不搞那么多花里胡哨的了


import logging
import time
import yaml
import sys
import datetime
import _thread
import argparse
import os
import importlib
import inspect
from tui import TSR_UI
from typing import Dict,Callable,List,Any, Union, Optional 
sys.path.append('..')
# TODO 确认下导入路径问题的原因和解决
sys.path.append(os.getcwd())
from base.testmodule.unitmaster import UnitMaster, WorkUnit
from modules.recorders import recorders
from plans import Plan,get_all_plans

# 配置日志输出
FORMAT = '%(asctime)s[%(levelname)s]%(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)
logger = logging.getLogger('tsrobot')


# 简单封装一下yaml，目的是统一配置文件的存放路径
class YamlConfig:
    default_config:Optional['YamlConfig'] = None
    def __init__(self, path):
        self.path = path
    
    @staticmethod
    def getDefault()->'YamlConfig':
        if YamlConfig.default_config is None:
            YamlConfig.default_config = YamlConfig('../testsuites/')
        return YamlConfig.default_config

    def loadf(self, fname):
        try:
            with open(self.path+fname+'.yaml','r') as f:
                res = yaml.load(f,Loader=yaml.FullLoader)
            return res
        except Exception as ex:
            return False
    
    def dumpf(self, fname, data):
        with open(self.path+fname+'.yaml','w') as f:
            res = yaml.dump(data,f)
        return res

class WorkModule:
    # 用例运行
    def __init__(self,unitmaster:UnitMaster):
        self.unitmaster = unitmaster
     
    def start(self):
        # 1. 循环do_work
        # 2. 发消息，结束
        logger.info('Work starts.')
        self.isrunning = True
        self.unitmaster.run()
        logger.info('Work end.')
        return

class Organizer:
    def __init__(self):
        self.cases = self.get_cases()
        self.plans = self.get_plans()
        self.extra_recorders = set()
        self.extra_recorders.add('console')
        
    def get_cases(self) -> List[WorkUnit]:
        cases = {}
        test_suites_path = 'testsuites/'
        # 遍历testsuites目录下的所有py文件
        for fname in os.listdir(test_suites_path):
            if fname.endswith('.py') and not fname.startswith('__'):
                module_name = fname[:-3]  # 去掉'.py'后缀
                full_module_name = f'testsuites.{module_name}'
                try:
                    module = importlib.import_module(full_module_name)
                    '''
                    unit = getattr(module, 'unit', None)
                    if isinstance(unit, WorkUnit):
                        cases[unit.id] = unit
                    '''
                    units = getattr(module,'units',None)
                    if type(units)==list:
                        for unit in units:
                            if isinstance(unit, WorkUnit):
                                cases[unit.id] = unit
                except ImportError as e:
                    logger.error(f'Failed to import module {full_module_name}: {e}')
                except AttributeError:
                    logger.error(f'Module {full_module_name} does not have a "unit" attribute.')
        return cases
    
    def get_plans(self):
        plans = {plan.id:plan for plan in get_all_plans('plans/')}
        return plans
    
    def run_case(self,case_id):
        master = UnitMaster().add_unit(self.cases[case_id])
        for recorder in self.extra_recorders:
            master.add_recorder(recorders[recorder])
        wm = WorkModule(master)
        wm.start()
        return
    
    def run_plan(self,plan_id):
        plan = self.plans[plan_id]
        cases = plan.cases
        for o_plans in plan.combined_plans:
            if o_plans.id==plan.id:
                continue
            cases += o_plans.cases
        if plan.unique:
            cases = list(set(cases))
        master = UnitMaster()
        for case_id in cases:
            if case_id not in self.cases:
                logger.error(f'测试用例{case_id}不存在')
                continue
            master.add_unit(self.cases[case_id])
        for recorder_name in plan.recorders:
            master.add_recorder(recorders[recorder_name])
        for recorder_name in self.extra_recorders:
            if recorder_name not in plan.recorders:
                master.add_recorder(recorders[recorder_name])
        wm = WorkModule(master)
        wm.start()
        return
    
    def add_extra_recorders(self,recorder_names:List[str]):
        for recorder_name in recorder_names:
            if recorder_name not in recorders:
                logger.error(f'记录器{recorder_name}不存在')
                continue
            self.extra_recorders.add(recorder_name)
        return


if __name__ == '__main__':
    # 处理下可能的外部参数吧
    # 暂时只考虑debug一个外部参数，其他的后续再慢慢考虑
    parser = argparse.ArgumentParser(description='性能用例自动化执行')
    parser.add_argument('-d','--debug',action='store_true',help='进入debug模式')
    parser.add_argument('-c','--casename',default=None,help='执行特定单个测试用例')
    parser.add_argument('-p','--planname',default=None,help='执行特定测试计划')
    parser.add_argument('-r','--recorders',default=[],nargs='+',help='指定结果记录器')
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    org = Organizer()
    cases = org.cases
    plans = org.plans
    if args.recorders:
        org.add_extra_recordders(args.recorders)
    if args.casename:
        test_case = cases.get(args.casename)
        if test_case:
            org.run_case(args.casename)
        else:
            logger.error(f'测试用例{args.casename}不存在')
        exit(0)
    if args.planname:
        test_plan = plans.get(args.planname)
        if test_plan:
            org.run_plan(args.planname)
        else:
            logger.error(f'测试计划{args.planname}不存在')
        exit(0)
    tui = TSR_UI()
    tui.on_case(org.run_case)
    tui.on_plan(org.run_plan)
    tui.set_cases([{'name':id,'description':case.description} for id,case in cases.items()])
    tui.set_plans([{'name':id,'description':plan.description} for id,plan in plans.items()])
    tui.main_menu()
