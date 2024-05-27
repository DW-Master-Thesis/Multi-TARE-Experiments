# pylint: disable=missing-module-docstring,missing-function-docstring

import pathlib
import itertools
import random

import fire
import yaml


def main(configs_dir: str = "./configs", world_name: str = "indoor"):
  configs_dir = pathlib.Path(configs_dir)

  world_configs_dir = configs_dir / world_name

  raw_positions_file = world_configs_dir / "raw_positions.txt"
  positions = load_positions(raw_positions_file)
  print(f"Loaded {len(positions)} positions")

  for num_robots in range(1, 6):
    random_position_combinations = sample_positions(positions, num_robots, 5)
    for i, position_combination in enumerate(random_position_combinations):
      config = positions_to_config(position_combination)
      config_file = world_configs_dir / f"{num_robots}_{i}.yaml"
      with open(config_file, "w", encoding="utf-8") as file:
        yaml.dump(config, file)


def load_positions(positions_file: str) -> list[tuple[float, float]]:
  with open(positions_file, "r", encoding="utf-8") as file:
    raw_positions = file.read()
    raw_positions = raw_positions.split("---\n")
    raw_positions = [yaml.safe_load(position) for position in raw_positions]

  positions = []
  for position in raw_positions:
    if not position:
      continue
    positions.append((position["point"]["x"], position["point"]["y"]))

  return positions


def sample_positions(
    positions: list[tuple[float, float]],
    num_robots: int,
    num_samples: int,
  ) -> list[list[tuple[float, float]]]:
  position_combinations = list(itertools.combinations(positions, num_robots))
  random_position_combinations = random.sample(position_combinations, num_samples)
  return random_position_combinations


def positions_to_config(positions: list[tuple[float, float]]) -> dict[str, dict[str, float]]:
  config = {}
  for robot_id, position in enumerate(positions):
    robot_name = f"robot_{robot_id}"
    config[robot_name] = {
        "vehicleHeight": 0.75,
        "cameraOffsetZ": 0.0,
        "vehicleX": position[0],
        "vehicleY": position[1],
        "vehicleZ": 0.0,
        "terrainZ": 0.0,
        "vehicleYaw": 0.0,
    }
  return config


if __name__ == "__main__":
  fire.Fire(main)
