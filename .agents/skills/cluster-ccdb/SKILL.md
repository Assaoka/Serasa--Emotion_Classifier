---
name: cluster-ccdb
description: >
  Use this skill whenever the user is working on an Alliance Canada HPC cluster
  (Narval, Nibi, Rorqual, Fir, Trillium) via SSH. Triggers include: writing or
  editing Slurm job scripts, requesting GPU resources, setting up Python environments,
  submitting or monitoring jobs, troubleshooting cluster errors, or any task that
  implies running code on a remote HPC environment. If the user mentions sbatch,
  squeue, modules, virtualenv on a server, or cluster-related paths like /project or
  $SCRATCH, use this skill immediately.
---

# Alliance Canada HPC Clusters

General documentation: https://docs.alliancecan.ca/wiki/Technical_documentation

## Step 0 — Identify the Active Cluster

Before writing any job script or giving cluster-specific advice, determine which
cluster you're on. Run:

```bash
hostname
```

Map the output to a cluster:

| hostname contains | Cluster   |
|-------------------|-----------|
| `narval`          | Narval    |
| `nibi`            | Nibi      |
| `rorqual`         | Rorqual   |
| `fir`             | Fir       |
| `trillium`        | Trillium  |

If `hostname` is ambiguous, also try `echo $SLURM_CLUSTER_NAME` or check
`/etc/hostname`. If still unclear, ask the user.

Keep the identified cluster in mind for the rest of the session — GPU specifiers
and available resources differ per cluster (see GPU section below).

---

## ⚠️ Critical: Job Queue Latency

> **Submitted jobs can take hours to start.** Slurm queues jobs; execution time
> depends on cluster load and the resources requested.

**Do:**
- Submit the job, note the Job ID, and stop
- Say the Job ID for reference
- Wait for the user to return with output or an error

**Do NOT:**
- Poll `squeue` or `sacct` in a loop
- Use timers or `watch` commands to track progress
- Assume a job failed because it hasn't started yet
- Check `slurm-{JOB_ID}.out` unless the user **explicitly** asks.
- Run monitoring commands unless the user **explicitly** asks.

Unnecessary polling wastes tokens and API budget.

---

## Job Submission (Slurm)

📖 https://docs.alliancecan.ca/wiki/Running_jobs

All jobs must go through Slurm via `sbatch`. Exception: tasks under ~10 min CPU
and ~4 GB RAM may run directly on the login node.

```bash
$ sbatch job.sh
```

### Minimal job script

```sh
#!/bin/bash
#SBATCH --time=00:15:00
#SBATCH --account=def-emilios

echo 'Hello, world!'
sleep 30
```

On GP clusters this reserves 1 core + 256 MB RAM. On Trillium, entire nodes are
always allocated (no partial allocation).

Output is written to `slurm-{JOB_ID}.out` in the submission directory by default.
The Job ID in the filename is required — it makes debugging much easier.

### Time format

`MM` | `MM:SS` | `HH:MM:SS` | `D-HH` | `D-HH:MM` | `D-HH:MM:SS`

Shorter wall times allow jobs to start faster (they fit on more nodes in the queue).

### Memory

- `--mem-per-cpu` — per core
- `--mem` — per node
- Default on GP clusters: 256 MB/core (omit if that's enough)
- Trillium: full node memory always allocated, no need to specify

### Job arrays

```sh
#!/bin/bash
#SBATCH --account=def-emilios
#SBATCH --time=0-0:5
#SBATCH --array=1-10
./myapplication $SLURM_ARRAY_TASK_ID
```

Creates 10 tasks with `$SLURM_ARRAY_TASK_ID` ranging from 1 to 10.

---

## GPU Jobs

📖 https://docs.alliancecan.ca/wiki/Using_GPUs_with_Slurm

Request GPUs with:

```sh
#SBATCH --gpus-per-node=<specifier>:<count>
```

### Available GPUs by cluster

**Narval** — A100 40 GB

| Specifier        | Type    | VRAM  |
|------------------|---------|-------|
| `a100`           | Full    | 40 GB |
| `a100_1g.5gb`    | MIG 1/8 | 5 GB  |
| `a100_2g.10gb`   | MIG 2/8 | 10 GB |
| `a100_3g.20gb`   | MIG 2/8 | 20 GB |
| `a100_4g.20gb`   | MIG 4/8 | 20 GB |

**Fir** — H100 80 GB

| Specifier                        | Type    | VRAM  |
|----------------------------------|---------|-------|
| `h100`                           | Full    | 80 GB |
| `nvidia_h100_80gb_hbm3_1g.10gb`  | MIG 1/8 | 10 GB |
| `nvidia_h100_80gb_hbm3_2g.20gb`  | MIG 2/8 | 20 GB |
| `nvidia_h100_80gb_hbm3_3g.40gb`  | MIG 3/8 | 40 GB |

**Nibi / Rorqual** — H100 80 GB (both share identical config)

| Specifier              | Alias         | Type    | VRAM  |
|------------------------|---------------|---------|-------|
| `h100`                 |               | Full    | 80 GB |
| `h100_10gb`            | `h100_1.10`   | MIG 1/8 | 10 GB |
| `h100_20gb`            | `h100_2.20`   | MIG 2/8 | 20 GB |
| `h100_40gb`            | `h100_3.40`   | MIG 3/8 | 40 GB |

**Nibi only:** also has `mi300a` (AMD MI300A, 128 GB).

**Trillium** — full node allocation only; check docs for current GPU spec.

---

## Email Notifications

📖 https://docs.alliancecan.ca/wiki/Running_jobs#Email_notification

```sh
#SBATCH --mail-user=joao.assaoka@unifesp.br
#SBATCH --mail-type=ALL
```

Options for `--mail-type`: `BEGIN`, `END`, `FAIL`, `ALL`. Use `ALL` if not specified by user.

---

## Python & Virtual Environments

📖 https://docs.alliancecan.ca/wiki/Python

### Load a Python module

```sh
# List available versions
module avail python

# Load your chosen version
module load python/3.13
```

Use the latest available version unless your code requires a specific one.

### Always use a virtual environment

Create it in `~/` or `/project/`. **Never under `$SCRATCH`** — files there can
be partially deleted by the system.

```sh
python -m venv ~/my_env
source ~/my_env/bin/activate
pip install <packages>
```

### AI / vLLM workloads

Compute nodes have **no internet access**. Always create and populate the virtual
environment from the **login node**, then only activate it inside the Slurm script.

For vLLM specifically, `opencv-python-headless` requires system modules to be
loaded first — skip this and the install will fail silently:

```sh
# On the login node, before pip install:
module load python/3.11
module load gcc opencv arrow
```

Packages not in the cluster's local wheelhouse (e.g. `mergekit`) will be
downloaded from PyPI — another reason to set up the env on the login node.

### Reference job script — AI/GPU workload

```sh
#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --account=def-emilios
#SBATCH --gpus-per-node=a100:1        # adjust specifier for your cluster
#SBATCH --mem=32G
#SBATCH --mail-user=joao.assaoka@unifesp.br
#SBATCH --mail-type=ALL

# 1. Load system modules (must match what was used when creating the venv)
module load python/3.11
module load gcc opencv arrow

# 2. Activate the virtual environment (created on the login node)
source ~/env_eniac/bin/activate

# 3. Disable network access — compute nodes have no internet
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONUNBUFFERED=1

# 4. Run your script
python src/models/train_relisa.py --model_id Polygl0t/Tucano2-qwen-0.5B-Instruct
```

A helper script at `setup_env.sh` (repo root) automates environment creation:

```bash
# Run from the repo root on the login node only
$ ./setup_env.sh
# Creates ~/env_eniac and installs all dependencies from requirements.txt
```

---

## Monitoring Jobs

📖 https://docs.alliancecan.ca/wiki/Monitoring_jobs

Only run these when the user explicitly asks:

```bash
# Jobs currently in queue or running
sq

# Detailed info on a finished job
sacct -j <JOB_ID> --format=JobID,State,ExitCode,Elapsed,MaxRSS

# Cancel a job
scancel <JOB_ID>
```