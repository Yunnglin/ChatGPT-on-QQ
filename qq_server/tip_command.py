from typing import Callable, List
from qq_server.express_package import express_package
from qq_server.bot import ServerBot

_all_scope = globals()
_excludes = set(['TipCommandManager', 'all_scope', 'excludes', 'tip', 'Callable', 'List', 'express_package', 'ServerBot'])

_help_cache = {}
_type_desc = {
    int: 'int',
    str: 'str',
    bool: 'bool'
}


def url_image(bot: ServerBot, url: str) -> str:
    return '[CQ:image,file={}]'.format(url)

def expression(bot: ServerBot) -> str:
    return url_image(express_package.random_url)

def clear_cache(bot: ServerBot) -> str:
    bot.talk_pool.clear_memory()
    return '已遗忘历史对话记录，我们重新开始交流吧 喵~'

def help(bot: ServerBot) -> str:
    help_string = '@Me tip.command.<command_name> <...args>\n'
    help_string += '可用指令(command_name):\n\n'
    if len(_help_cache) == 0:
        for name, value in _all_scope.items():
            if isinstance(value, TipCommandManager):
                continue
            if not name.startswith('_') and name not in _excludes:

                command_name = name
                command_func: Callable = value
                args_desc = ''
                for arg_name, arg_type in list(command_func.__annotations__.items())[1:]:
                    if arg_name == 'return':
                        continue
                    args_desc += ' {}({})'.format(arg_name, _type_desc[arg_type])
                args_desc = args_desc.strip()
                if len(args_desc) == 0:
                    args_desc = '无参数'
                _help_cache[command_name] = args_desc

    for command_name, args_desc in _help_cache.items():
        help_string += "\t{} {}\n".format(command_name, args_desc)
        
    return help_string


class TipCommandManager:
    command_functions = {}
    def __init__(self) -> None:
        for name, value in _all_scope.items():
            if isinstance(value, TipCommandManager):
                continue
            if not name.startswith('_') and name not in _excludes:
                self.command_functions.__setitem__(name, value)        
    

    def has_command(self, command_name: str) -> bool:
        return command_name in self.command_functions

    def get_tip_command_function(self, command_name) -> Callable:
        command_func = self.command_functions.get(command_name, None)
        return command_func

    def exec_tip_command(self, command_name: str, args: List[str]) -> str:
        """
        args首位为bot自身
        """
        true_args = [args[0]]
        
        exec_func = self.get_tip_command_function(command_name)
        if exec_func is None:
            return '指令错误: {}不在command中'.format(command_name)
        exec_func_annotations = {k : v for k, v in exec_func.__annotations__.items() if k != 'return'}

        if len(args) != len(exec_func_annotations):
            return '参数错误: 应该接受的参数数量：{}，实际接受参数数量：{}'.format(len(exec_func.__annotations__), len(args))        
        
        for arg_name, arg_type in list(exec_func_annotations.items())[1:]:
            index = len(true_args)
            try:
                true_args.append(arg_type(args[index]))
            except Exception as e: 
                return '在转换参数{}时发生错误，请检查是否类型出错（正确类型:{}）Error:{}'.format(args[index], _type_desc[arg_type], e)
        
        try:
            res = exec_func(*true_args)
            return res
        except Exception as e:
            return 'ERROR发生:{}'.format(e)


commmand_mananger = TipCommandManager()