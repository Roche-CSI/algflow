import dataclasses
import logging
import shlex
import subprocess
from timeit import default_timer

from algflow import Algorithm

logger = logging.getLogger(__name__)


def safe_decode(s):
    if s is None:
        return None
    return s.decode()


@dataclasses.dataclass
class ExecutionResult:
    return_code: int
    stdout: str
    stderr: str
    runtime: float


class Process:
    def __init__(self, cmd, timeout=None):
        self.cmd = cmd
        self.timeout = timeout
        self.start_time = default_timer()
        self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @property
    def exe_name(self):
        return self.cmd[0]

    def timeout_reached(self):
        return self.timeout is not None and default_timer() - self.start_time >= self.timeout

    def report_progress(self):
        elapsed_time = default_timer() - self.start_time
        if elapsed_time % 20 == 0:
            logger.debug(f'{self.exe_name} running for {elapsed_time} secs.')

    def kill_process_and_raise_timeout(self):
        self.process.kill()
        msg = f'{self.exe_name} timed out at {self.timeout} secs.'
        raise TimeoutError(msg)

    def communicate(self) -> ExecutionResult:
        # periodically check if the process is still running
        while self.process.poll() is None:
            if self.timeout_reached():
                self.kill_process_and_raise_timeout()
            else:
                self.report_progress()

        stdout, stderr = self.process.communicate()
        runtime = default_timer() - self.start_time
        logger.debug(f'{self.exe_name} completed: {runtime} secs')

        return ExecutionResult(self.process.returncode, safe_decode(stdout), safe_decode(stderr), runtime)


class CmdLineAlgorithm(Algorithm):
    def cmd(self) -> str:
        raise NotImplementedError('This method must be implemented')

    def pre_run(self, inputs, cmd):
        pass

    def post_run(self, exec_result, inputs, output):
        pass

    def run(self, inputs, outputs):
        cmd = self.cmd()
        if not cmd:
            raise ValueError('cmd is empty')
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)

        self.pre_run(input, cmd)
        process = Process(cmd)
        exec_result = process.communicate()
        self.post_run(exec_result, inputs, outputs)
