class WorkerRouter():
    @classmethod
    def from_id(cls, worker_id:int):
        """Calls Autoppia Infra module and get the IP:port of the worker"""
        ip, port = get_ip_and_port_from_infra_layer()
        return cls(ip, port)
    
    def call(worker_id):
        pass
        
    