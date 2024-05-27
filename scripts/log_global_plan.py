# pylint: disable=missing-module-docstring, missing-function-docstring,consider-using-with,line-too-long,too-many-arguments
import os
import shlex
import subprocess
import time

import fire


def main(output_dir="./global_plan", namespace="default", num_robots=2, timeout=3600):
  processes = []
  output_dir = os.path.join(output_dir, namespace)
  processes.extend(start_log_global_plan_processes(namespace, output_dir, num_robots))

  time.sleep(timeout)
  for process in processes:
    try:
      os.kill(process.pid, 2)
    except ProcessLookupError as e:
      print(e)


def start_log_global_plan_processes(namespace: str, logs_dir: str, num_robots: int):
  processes = []
  for i in range(num_robots):
    start_record_global_plan = f"ros2 topic echo -f /{namespace}/robot_{i}/distance_matrix"
    processes.append(start_and_log_process(start_record_global_plan, logs_dir, f"record_global_plan_{i}"))
  return processes


def start_and_log_process(command: str, logs_dir: str, process_name: str):
  logs_file = os.path.join(logs_dir, f"{process_name}.log")
  with open(logs_file, "w", encoding="utf-8") as f:
    return subprocess.Popen(shlex.split(command), stdout=f, stderr=subprocess.STDOUT)


if __name__ == "__main__":
  fire.Fire(main)
