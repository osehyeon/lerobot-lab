# lerobot-lab

A personal lab for studying and experimenting with Vision-Language-Action (VLA) models.
It builds on [LeRobot](https://github.com/huggingface/lerobot) and uses the SO-101 arm as the reference robot.

The repo has two parts:

- **`docs/`** — notes on LeRobot, imitation learning, VLA lineage, benchmarks, quantization and hardware
- **`scripts/`** — an SO-101 MuJoCo simulation that runs on a Mac, plus a keyboard teleop script

Training and inference run on a CUDA GPU server. The Mac is for reading code, writing notes and scripts,
and MuJoCo simulation only.

## Quickstart

```bash
git clone git@github.com:osehyeon/lerobot-lab.git
cd lerobot-lab

bash scripts/so101_sim_setup.sh             # venv, MuJoCo, so101-nexus, SO-101 model
python3 scripts/so101_teleop.py             # drive the SO-101 by keyboard
```

The setup script is idempotent: rerunning it skips whatever is already in place, and it finishes by
resetting, stepping and rendering all six environments. Downloads and the venv go into `scripts/_so101/`,
which is gitignored.

## Contents

| Path | |
|---|---|
| `scripts/so101_sim_setup.sh` | Creates the venv, installs [so101-nexus](https://github.com/johnsutor/so101-nexus) `0.5.4`, fetches the SO-101 MJCF and STL meshes, verifies |
| `scripts/so101_teleop.py` | Drive an SO-101 task by keyboard. Nothing is recorded |
| `docs/` | 12 notes, listed below. Written in Korean |
| `CLAUDE.md` | Working rules and environment notes |

## Drive it yourself

```bash
python3 scripts/so101_teleop.py                              # MuJoCoTouch-v1, the easiest
python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # lift the cube
python3 scripts/so101_teleop.py --task MuJoCoStackCube-v1 --seed 3
```

Run it with any `python3`. It re-execs itself under `scripts/_so101/.venv`, and on macOS under `mjpython`,
which the viewer needs.

| Key | |
|---|---|
| `w` `s` / `a` `d` / `r` `f` | move the end effector along x / y / z |
| `z` `x` / `t` `g` / `c` `v` | rotate about x / y / z |
| `space` | toggle gripper |
| `q` | reset the task (new layout) |
| `ctrl-c` | quit |

- **Keys are read from the terminal, not the viewer window.** The MuJoCo viewer already binds space,
  backspace, the digits and most letters as shortcuts. After rotating the camera in the viewer, click the
  terminal again. No macOS Accessibility permission is needed
- Right after a reset the end effector sits 6 cm above the floor, so `f` barely moves it. Lift with `r` first
- The SO-101 arm has five joints. Rotation about x and y works; rotation about z mixes with x, and any
  rotation shifts the end effector by a few centimetres

| Option | |
|---|---|
| `--task` | `MuJoCoTouch-v1` (default), `MuJoCoPickLift-v1`, `MuJoCoPickAndPlace-v1`, `MuJoCoStackCube-v1`, `MuJoCoLookAt-v1`, `MuJoCoMove-v1` |
| `--pos-sensitivity` / `--rot-sensitivity` | translation / rotation speed, default 0.15 / 0.2 |
| `--hold` | how long one keypress keeps moving, default 0.15 s. Raise it if holding a key stutters |
| `--demo` | play a fixed key sequence in the viewer, no keyboard needed |
| `--selftest` | measure each key's translation and rotation without a viewer |

Measurements and the control scheme are in [docs/so101-sim.md](docs/so101-sim.md).

### Viewer only

Use the command the setup script prints at the end:

```bash
DYLD_LIBRARY_PATH=<uv Python lib dir> scripts/_so101/.venv/bin/mjpython \
  -m mujoco.viewer --mjcf=scripts/_so101/scene.xml
```

The standalone Python that uv installs keeps `libpython` in its own install directory, while `mjpython`
only looks next to the venv's `bin/python`, so it needs `DYLD_LIBRARY_PATH`. A venv built from Homebrew's
`python3.12` does not.

## Notes

All notes are in Korean.

**Concepts**

| Note | |
|---|---|
| [lerobot.md](docs/lerobot.md) | What LeRobot is |
| [imitation-learning.md](docs/imitation-learning.md) | Imitation learning — the three core problems of behavior cloning and their fixes |
| [mpc-act-rtc.md](docs/mpc-act-rtc.md) | MPC → ACT → RTC, explained for non-specialists |

**Models**

| Note | |
|---|---|
| [policies.md](docs/policies.md) | Policies supported by LeRobot, action representations, VRAM and training time |
| [vla-lineage.md](docs/vla-lineage.md) | VLA paper lineage, from RT-2 to 2026 |

**Evaluation**

| Note | |
|---|---|
| [vla-benchmarks.md](docs/vla-benchmarks.md) | Lineage of evaluation datasets and benchmarks |
| [vla-replica.md](docs/vla-replica.md) | VLA-REPLICA — a real-world SO-101 benchmark with 501 human demonstrations |

**Quantization**

| Note | |
|---|---|
| [vla-quantization.md](docs/vla-quantization.md) | Lineage of VLA quantization papers |
| [training-free-trend.md](docs/training-free-trend.md) | Why "training-free" became common |
| [quantization-experiment-plan.md](docs/quantization-experiment-plan.md) | Experiment plan — SmolVLA and π0.5 on LIBERO and LIBERO-Plus |

**Hardware and simulation**

| Note | |
|---|---|
| [lerobot-hardware.md](docs/lerobot-hardware.md) | Robots and teleoperators LeRobot supports |
| [so101-sim.md](docs/so101-sim.md) | SO-101 MuJoCo model, so101-nexus tasks, keyboard teleop |

## Papers

`paper/` is gitignored. The two LeRobot papers the notes refer to come from arXiv:

```bash
mkdir -p paper
curl -L -o paper/2602.22818-lerobot-library.pdf        https://arxiv.org/pdf/2602.22818
curl -L -o paper/2510.12403-robot-learning-tutorial.pdf https://arxiv.org/pdf/2510.12403
```

## License

MIT — see [LICENSE](LICENSE).

The scripts download third-party code and data that are not part of this repo:

| | License |
|---|---|
| [so101-nexus](https://github.com/johnsutor/so101-nexus) | Apache-2.0, pinned to `0.5.4` on PyPI |
| [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) `Simulation/SO101` | as stated in the upstream repo |
| MuJoCo | Apache-2.0 |
