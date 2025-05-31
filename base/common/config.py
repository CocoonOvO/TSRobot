import yaml
import os

# 定义配置类
# 暂时废弃

class Config:
    _instances = {}
    _default_path = os.path.join(os.path.dirname(__file__), '../../conf')
    _default_file = 'config.yaml'

    def __new__(cls, *args, **kwargs):
        path = kwargs.get("path", cls._default_path)
        file = kwargs.get("file", cls._default_file)
        config_file_path = os.path.join(path, file)
        if config_file_path in cls._instances:
            return cls._instances[config_file_path]
        else:
            instance = super().__new__(cls)
            instance.file_path = config_file_path
            cls._instances[config_file_path] = instance
            return instance

    def __init__(self, file=None, path=None):
        self.path = str(path or self._default_path)
        self.file = file or self._default_file
        self.file_path = os.path.join(self.path, self.file)

    def get(self, key, default=None):
        """获取配置项"""
        if not hasattr(self,'config'):
            self.read()
        return self.config.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        if not hasattr(self,'config'):
            self.read()
        self.config[key] = value

    def read(self):
        """从文件中读取配置信息"""
        try:
            with open(self.file_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            with open(self.file_path, "w") as f:
                yaml.dump({}, f)
            self.config = {}

    def write(self):
        """将配置信息写入文件"""
        with open(self.file_path, "w") as f:
            yaml.dump(self.config, f)

    def commit_changes(self):
        """将修改后的配置项写入文件"""
        if hasattr(self,'config'):
            self.write()

    def __enter__(self):
        """实现上下文管理器，用于支持 with 语句"""
        self.read()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """退出上下文管理器时自动提交修改"""
        self.commit_changes()