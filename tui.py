# 这是一个tui界面，帮我先用rich实现，注意适当美化。可以使用art增强标题等艺术字效果
# 大标题是TSRobot,这也是这个程序的名字，需要使用合适的艺术字
# 主页面有三个选项，测试用例、测试计划和离开
# case页面会以多列形式列举一批测试用例名称和对应描述(如果描述是空则为-)，然后有两个选项，运行测试用例和返回上一页。如果允许则需要输入测试用例名。
# plan页面与case页面类似，但展示得到是一批测试计划的名称和对应描述，同样有允许测试计划和返回上一页两个选择，允许则需要输入测试计划名
# 退出时需要确认是否退出，确认后退出程序
# 用例/计划运行结束后，有一行完成提示，有返回上一级（也就是用例/计划列表）的选项
# 测试用例和测试计划的具体内容暂不实现，先自行生成一批测试用例和测试计划即可。需要注意留有合适的接口方便后续将实际的测试用例/计划接入
# 同样的，执行用例/计划的部分不需要实现具体执行，pass后直接进入执行完成的页面就行

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from art import text2art
import sys

console = Console()

class TSR_UI:
    def __init__(self):
        self.test_cases = [
            {"name": "测试用例1", "description": "这是第一个测试用例的描述"},
            {"name": "测试用例2", "description": "-"},
            {"name": "测试用例3", "description": "这是第三个测试用例的描述"},
        ]
        self.test_plans = [
            {"name": "测试计划1", "description": "这是第一个测试计划的描述"},
            {"name": "测试计划2", "description": "-"},
            {"name": "测试计划3", "description": "这是第三个测试计划的描述"},
        ]
    
    def set_cases(self,cases):
        self.test_cases = cases
    
    def set_plans(self,plans):
        self.test_plans = plans
    
    def on_case(self,func):
        self.case_func = func
    
    def on_plan(self,func):
        self.plan_func = func

    def main_menu(self):
        while True:
            console.clear()
            console.print(text2art("TSRobot"), style="bold blue")
            console.print("[bold]请选择一个选项:[/bold]")
            console.print("1. 测试用例")
            console.print("2. 测试计划")
            console.print("3. 离开")
            
            choice = Prompt.ask("输入选项编号", choices=["1", "2", "3"])
            
            if choice == "1":
                self.case_menu()
            elif choice == "2":
                self.plan_menu()
            elif choice == "3":
                if console.input("确认要退出程序吗？(y/n): ").lower() == "y":
                    sys.exit("退出程序")
                else:
                    continue

    def case_menu(self):
        while True:
            console.clear()
            console.print("[bold]测试用例列表:[/bold]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("名称", style="dim")
            table.add_column("描述")
            
            for case in self.test_cases:
                table.add_row(case["name"], case["description"])
            
            console.print(table)
            console.print("1. 运行测试用例")
            console.print("2. 返回上一页")
            
            choice = Prompt.ask("输入选项编号", choices=["1", "2"])
            
            if choice == "1":
                case_name = Prompt.ask("请输入测试用例名称")
                if any(case["name"] == case_name for case in self.test_cases):
                    console.print(f"测试用例 {case_name} 正在运行...")
                    # 这里可以添加运行测试用例的具体逻辑，暂时使用pass
                    self.case_func(case_name)
                    console.print(f"[bold green]测试用例 {case_name} 完成[/bold green]")
                    console.print("按 Enter 返回上一级...")
                    console.input()
                else:
                    console.print("[bold red]测试用例名称不存在[/bold red]")
                    console.print("按 Enter 返回上一级...")
                    console.input()
            elif choice == "2":
                return

    def plan_menu(self):
        while True:
            console.clear()
            console.print("[bold]测试计划列表:[/bold]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("名称", style="dim")
            table.add_column("描述")
            
            for plan in self.test_plans:
                table.add_row(plan["name"], plan["description"])
            
            console.print(table)
            console.print("1. 运行测试计划")
            console.print("2. 返回上一页")
            
            choice = Prompt.ask("输入选项编号", choices=["1", "2"])
            
            if choice == "1":
                plan_name = Prompt.ask("请输入测试计划名称")
                if any(plan["name"] == plan_name for plan in self.test_plans):
                    console.print(f"测试计划 {plan_name} 正在运行...")
                    # 这里可以添加运行测试计划的具体逻辑，暂时使用pass
                    self.plan_func(plan_name)
                    console.print(f"[bold green]测试计划 {plan_name} 完成[/bold green]")
                    console.print("按 Enter 返回上一级...")
                    console.input()
                else:
                    console.print("[bold red]测试计划名称不存在[/bold red]")
                    console.print("按 Enter 返回上一级...")
                    console.input()
            elif choice == "2":
                return

if __name__ == "__main__":
    TSR_UI().main_menu()
