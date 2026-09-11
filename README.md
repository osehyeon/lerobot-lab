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
| `docs/` | 13 notes, listed below. Written in Korean |
| `CLAUDE.md` | Working rules and environment notes |

## Drive it yourself

```bash
python3 scripts/so101_teleop.py                              # MuJoCoTouch-v1, the easiest
python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # lift the cube
python3 scripts/so101_teleop.py --task MuJoCoStackCube-v1 --seed 3
```

Run it with any `python3`; it re-execs itself under `scripts/_so101/.venv`. It prints the key table to the
terminal on start.

It opens one OpenCV window: a view from behind the base on the left, the wrist camera on the right, with
the instruction, the gripper position and state, and the keys currently held drawn on top.
**Keys go to that window** — click it once when it opens.

| Key | |
|---|---|
| `w` `s` / `a` `d` / `r` `f` | move the end effector along x / y / z — away and back, left and right, up and down on screen |
| `z` `x` / `t` `g` / `c` `v` | rotate about x / y / z |
| `space` | toggle gripper |
| `q` | reset the task (new layout) |
| `esc` | quit, or close the window |

The SO-101 arm has five joints. Rotation about x and y works; rotation about z mixes with x, and any
rotation shifts the end effector by a few centimetres.

| Option | |
|---|---|
| `--task` | `MuJoCoTouch-v1` (default), `MuJoCoPickLift-v1`, `MuJoCoPickAndPlace-v1`, `MuJoCoStackCube-v1`, `MuJoCoLookAt-v1`, `MuJoCoMove-v1` |
| `--view` | `angled` (default, from behind the base) or `overhead` (the straight-down camera the policy sees) |
| `--pos-sensitivity` / `--rot-sensitivity` | translation / rotation speed, default 0.15 / 0.2 |
| `--rotation-weight` | IK weight on orientation while a rotation key is held, default 0.1 |
| `--hold` | how long one keypress keeps moving, default 0.15 s. Raise it if holding a key stutters |
| `--fps` | how often the window redraws, default 20. Physics runs at 50 Hz regardless |
| `--no-wrist` | drop the wrist view, which halves the render cost |
| `--mujoco-viewer` | use the MuJoCo viewer instead, with a mouse-orbit camera. Keys are then read from the terminal |
| `--demo` | play a fixed key sequence, no keyboard needed |
| `--selftest` | measure each key's translation and rotation without a window |
| `--snapshot PNG` | save one window frame and exit |

### Why the angled view

The environment's own camera looks straight down, so moving up 8.6 cm with `r` shows as 1.3 cm on screen,
and only `a` `d` — which swing the whole arm about its base — look like they move anything.

### Why the IK orientation weight changes

Moving uses the package default of 0.01; holding a rotation key raises it to 0.1. At 0.01 the rotation keys
barely turn the gripper. At 0.1, moving from the folded reset pose pins `shoulder_lift` at its −100° limit
and bends only the wrist, so `f` lifts the gripper instead of lowering it.

### Why not the MuJoCo viewer

The MuJoCo viewer binds all 26 letters to visualization shortcuts. `w` `s` `r` `g` toggle wireframe,
shadow, reflection and fog, so typing into the viewer moves the arm *and* changes the rendering, and the
passive viewer does not expose those flags to undo them. With `--mujoco-viewer`, type in the terminal,
not in the viewer window.

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
| [so101-purchase.md](docs/so101-purchase.md) | Where to buy an SO-101, cameras and camera mounts — vendors, contents, prices |

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
