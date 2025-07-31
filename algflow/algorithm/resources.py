from dataclasses import dataclass


@dataclass
class ResourceSchema:
    cpu: int
    gpu_count: int
    memory: str
    storage: str

@dataclass
class Trace:
    task_id: str
    hash: str
    native_id: str
    name: str
    status: str

    fields = 'task_id,hash,native_id,name,status,exit,submit,duration,realtime,%cpu,peak_rss,peak_vmem,rchar,read_bytes,wchar,write_bytes,disk'


