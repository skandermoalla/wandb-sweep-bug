import logging
import subprocess
import sys
from pathlib import Path
from time import sleep

import hydra
import wandb
from omegaconf import DictConfig, OmegaConf, omegaconf

logger = logging.getLogger(__name__)

@hydra.main(version_base=None, config_path=".", config_name="hydra")
def main(config: DictConfig) -> None:
    run = wandb.init(
        id=str(config.n),
        resume="allow",
        config=OmegaConf.to_container(config),
        project=config.wandb_project,
    )
    logger.info(f"Running command: {subprocess.list2cmdline(sys.argv)}")
    logger.info(f"Working directory: {Path.cwd()}")
    logger.info(f"Running with config: \n{OmegaConf.to_yaml(config)}")

    files = sorted(Path.cwd().glob("file_*.txt"), key=lambda x: int(x.stem.split("_")[1]))
    if files:
        last_file = files[-1]
        logger.info(f"Resuming from {last_file}")
        i = int(last_file.stem.split("_")[1])
    else:
        i = -1

    steps = 0
    while True:
        i += 1

        # Compute and log x**n.
        y = i**config.n
        logs = {"i": i, "y": y}
        print(logs)
        wandb.log(logs)

        # Checkpoint every 5 steps.
        if i % 5 == 0:
            with open(f"file_{i}.txt", "w") as f:
                f.write(f"y={y}")
                print(f"Checkpointing at {i}")

        steps += 1
        # Preempt every 13 steps.
        if steps == 13:
            run.mark_preempting()
            raise InterruptedError("Preempt after 13 steps.")

        sleep(1)


if __name__ == "__main__":
    main()
