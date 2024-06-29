# pylint: disable=missing-module-docstring, missing-function-docstring,consider-using-with,line-too-long,too-many-arguments
import os
import shlex
import subprocess
import time

import fire
import numpy as np
import yaml


def main(logs_dir="./logs", configs_dir="./configs", world_name="indoor", timeout: int = 3600):
  for num_robots in [2]:
    for delay_time in [10]:
      for i in range(1):
        print("#######################")
        print(f"Starting experiment {i}")
        print("#######################")
        agents_configs_file = create_agents_configs_file(configs_dir, world_name, num_robots)
        start_processes(logs_dir, world_name, agents_configs_file, delay_time, num_robots, timeout)
        print("#######################")
        print(f"Experiment {i} finished")
        print("#######################")
        time.sleep(10)


def create_agents_configs_file(configs_dir: str, world_name: str, num_robots: int) -> str:
  keypose_graph_file = os.path.join(configs_dir, world_name, "keypose_graph.npy")
  keypose_graph = np.load(keypose_graph_file)
  config = {}
  random_selection = np.random.randint(0, keypose_graph.shape[0] - num_robots)

  for robot_id in range(num_robots):
    robot_name = f"robot_{robot_id}"
    config[robot_name] = {
        "vehicleHeight": 0.75,
        "cameraOffsetZ": 0.0,
        "vehicleX": float(keypose_graph[robot_id + random_selection, 0]),
        "vehicleY": float(keypose_graph[robot_id + random_selection, 1]),
        "vehicleZ": float(keypose_graph[robot_id + random_selection, 2]),
        "terrainZ": 0.0,
        "vehicleYaw": 0.0,
    }

  config_file = os.path.join(configs_dir, world_name, f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.yaml")
  with open(config_file, "w", encoding="utf-8") as file:
    yaml.dump(config, file)
  print(f"Created config file: {config_file}")
  return config_file


def start_processes(
    logs_dir="./logs",
    world_name="indoor",
    agents_configs_file="./configs/indoor/2_1.yaml",
    delay_time: int = 1,
    num_robots: int = 2,
    timeout: int = 3600,
):
  # Create logs dir from curret time
  namespace = "experiment_" + time.strftime('%Y_%m_%d_%H_%M_%S')
  logs_dir = os.path.join(logs_dir, namespace)
  os.makedirs(logs_dir, exist_ok=True)

  # Start gazebo
  start_gazebo = f"ros2 launch vehicle_simulator gazebo.launch.py gui:=false worldName:={world_name}"
  start_vehicle_simulator = f"ros2 launch vehicle_simulator simulation_multi_agent.launch.py namespace:={namespace} agentsConfigFile:={agents_configs_file} worldName:={world_name}"
  start_merger = f"ros2 launch tare_planner planning_interface_merger.launch.py delay_time:={delay_time} num_robots:={num_robots} namespace:={namespace}"

  # Start the processes
  processes = []
  processes.append(subprocess.Popen(shlex.split(start_gazebo)))
  time.sleep(5)
  processes.append(subprocess.Popen(shlex.split(start_vehicle_simulator)))
  time.sleep(10)
  processes.append(start_and_log_process(start_merger, logs_dir, "planner"))
  processes.extend(start_planner_processes(namespace, logs_dir, get_num_robots(agents_configs_file)))

  # Wait for the processes to finish
  time.sleep(timeout)
  for process in processes:
    try:
      os.kill(process.pid, 2)
    except ProcessLookupError as e:
      print(e)


def start_planner_processes(namespace: str, logs_dir: str, num_robots: int):
  processes = []
  for i in range(num_robots):
    start_robot = f"ros2 launch tare_planner explore.launch.py namespace:={namespace} robotName:=robot_{i} rviz:=true configFile:=default numRobots:={num_robots}"
    processes.append(start_and_log_process(start_robot, logs_dir, f"robot_{i}"))
  return processes


def start_and_log_process(command: str, logs_dir: str, process_name: str):
  logs_file = os.path.join(logs_dir, f"{process_name}.log")
  with open(logs_file, "w", encoding="utf-8") as f:
    return subprocess.Popen(shlex.split(command), stdout=f, stderr=subprocess.STDOUT)


def get_num_robots(agents_configs_file: str):
  with open(agents_configs_file, "r", encoding="utf-8") as f:
    agents_configs = yaml.safe_load(f)
  return len(agents_configs)


if __name__ == "__main__":
  fire.Fire(main)
