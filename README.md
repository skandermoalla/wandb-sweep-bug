# W&B resuming sweep bug

Install the dependencies:

```bash
pip install -U wandb hydra-core
# Tested with python=3.10, wandb=0.19.1, hydra-core=1.3.2
```

Run a script:

The script computes and logs i**n for i>=0, checkpointing every 5 iterations and preempts every 13 iterations.

```bash
python main.py n=1
```

To resume a preempted run, rerun the script with the same arguments:

```bash
python main.py n=1
```

To create and start a sweep:
    
```bash
wandb sweep sweep.yaml
wandb agent <SWEEP_ID>
```

Runs are marked preempting before they preempt so the sweep knows to rerun them,
but it gives the wrong arguments to the agent to resume the runs so they crash before starting.

The bug:

When taking a new config from the sweep:
```bash
2024-12-25 18:20:06,293 - wandb.wandb_agent - INFO - Agent received command: run
2024-12-25 18:20:06,293 - wandb.wandb_agent - INFO - Agent starting run with config:
        n: 2
2024-12-25 18:20:06,296 - wandb.wandb_agent - INFO - About to run command: python main.py n=2
```

When resuming a preempted config from the sweep:
```bash
2024-12-25 18:20:32,249 - wandb.wandb_agent - INFO - Agent received command: resume
2024-12-25 18:20:32,250 - wandb.wandb_agent - INFO - Agent starting run with config:
        n: 2
        some_key_that_is_never_passed_as_argument_but_added_by_sweeps_when_resuming: {'some_subkey': 'foo'}
        wandb_project: wandb-sweep-bug
2024-12-25 18:20:32,253 - wandb.wandb_agent - INFO - About to run command: python main.py n=2 "some_key_that_is_never_passed_as_argument_but_added_by_sweeps_when_resuming={'some_subkey': 'foo'}" wandb_project=wandb-sweep-bug
no viable alternative at input '{'some_subkey''
See https://hydra.cc/docs/1.2/advanced/override_grammar/basic for details
```
