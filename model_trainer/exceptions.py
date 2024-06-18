class K8sException(Exception):
    def __init__(self, status, response) -> None:
        super().__init__(self)
        self.status = status
        self.response = response