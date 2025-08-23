import os
import time
import tempfile
import docker

class CodeJudge:
    """
    安全的代码评测类，使用Docker沙箱隔离执行用户代码。
    """
    LANG_CONFIG = {
        'python': {
            'source_file': 'main.py',
            'compile_cmd': None,
            'run_cmd': 'python3 main.py < {input_file}'
        },
        'c': {
            'source_file': 'main.c',
            'compile_cmd': 'gcc main.c -o main',
            'run_cmd': './main < {input_file}'
        },
        'cpp': {
            'source_file': 'main.cpp',
            'compile_cmd': 'g++ main.cpp -o main',
            'run_cmd': './main < {input_file}'
        }
    }

    def __init__(self,
                 docker_image='code-judge-env:latest',
                 mem_limit='128m',
                 cpu_quota=50000,  # 5% of a single CPU
                 cpu_period=1000000,
                 pids_limit=64,
                 timeout=10):
        self.docker_image = docker_image
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.cpu_period = cpu_period
        self.pids_limit = pids_limit
        self.timeout = timeout
        self.client = docker.from_env()

    def run_tests(self, code, language, test_cases):
        if language not in self.LANG_CONFIG:
            raise ValueError(f"Unsupported language: {language}")

        config = self.LANG_CONFIG[language]
        results = []

        with tempfile.TemporaryDirectory(prefix='judge_') as temp_dir:
            code_path = os.path.join(temp_dir, config['source_file'])
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(code)

            if config['compile_cmd']:
                compile_result = self._run_in_docker(
                    temp_dir=temp_dir,
                    command=config['compile_cmd'],
                    workdir='/usr/src/app',
                    stdin_file=None
                )
                if compile_result['exit_code'] != 0:
                    for idx, _ in enumerate(test_cases, 1):
                        results.append({
                            'id': idx,
                            'passed': False,
                            'output': '',
                            'error': compile_result['stderr'][:4096],
                            'time_used': 0.0
                        })
                    return results

            for idx, case in enumerate(test_cases, 1):
                input_file = os.path.join(temp_dir, f'input_{idx}.txt')
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(case['input'])

                run_cmd = config['run_cmd'].format(input_file=f'input_{idx}.txt')
                start_time = time.time()
                run_result = self._run_in_docker(
                    temp_dir=temp_dir,
                    command=run_cmd,
                    workdir='/usr/src/app',
                    stdin_file=None
                )
                time_used = round(time.time() - start_time, 3)

                output = (run_result['stdout'] or '').strip()
                expected = (case['expected_output'] or '').strip()
                passed = (output == expected) and run_result['exit_code'] == 0

                error_msg = ''
                if run_result['timeout']:
                    error_msg = 'Time Limit Exceeded'
                    passed = False
                elif run_result['oom_killed']:
                    error_msg = 'Memory Limit Exceeded'
                    passed = False
                elif run_result['exit_code'] != 0 and not run_result['timeout'] and not run_result['oom_killed']:
                    error_msg = run_result['stderr'][:4096] or 'Runtime Error'
                    passed = False

                results.append({
                    'id': idx,
                    'passed': passed,
                    'output': output,
                    'error': error_msg,
                    'time_used': time_used
                })

        return results

    def _run_in_docker(self, temp_dir, command, workdir, stdin_file=None):
        container = None
        try:
            volumes = {
                os.path.abspath(temp_dir): {
                    'bind': '/usr/src/app',
                    'mode': 'ro'
                }
            }
            container = self.client.containers.run(
                image=self.docker_image,
                command=['/bin/sh', '-c', command],
                working_dir=workdir,
                volumes=volumes,
                network_disabled=True,
                mem_limit=self.mem_limit,
                pids_limit=self.pids_limit,
                cpu_period=self.cpu_period,
                cpu_quota=self.cpu_quota,
                detach=True,
                stdout=True,
                stderr=True,
                remove=False,
                read_only=True,
                user='1000:1000'
            )
            try:
                exit_status = container.wait(timeout=self.timeout)
                exit_code = exit_status.get('StatusCode', -1)
                timeout_flag = False
            except Exception:
                container.kill()
                exit_code = -1
                timeout_flag = True
            try:
                stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
                stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
            except Exception:
                stdout, stderr = '', ''
            inspect = container.attrs
            oom_killed = inspect.get('State', {}).get('OOMKilled', False)
            return {
                'exit_code': exit_code,
                'stdout': stdout,
                'stderr': stderr,
                'timeout': timeout_flag,
                'oom_killed': oom_killed
            }
        except docker.errors.ContainerError as e:
            return {
                'exit_code': e.exit_status,
                'stdout': e.stdout.decode('utf-8', errors='ignore') if e.stdout else '',
                'stderr': e.stderr.decode('utf-8', errors='ignore') if e.stderr else '',
                'timeout': False,
                'oom_killed': False
            }
        except Exception as e:
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'timeout': False,
                'oom_killed': False
            }
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
