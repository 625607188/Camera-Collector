class SingletonBase():
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingletonBase, cls).__new__(cls)
        return cls._instance
