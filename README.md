# WSL & Remote Linux Development Notes

A reference guide covering WSL, remote SSH connections, and Linux-on-Windows options — based on hands-on exploration.

---

## Options for Running Linux Without a Dedicated Linux Machine

| Option | Difficulty | "Real" Linux Feel | Requires 2nd PC |
|--------|-----------|-------------------|-----------------|
| **WSL2 (local)** | Easy | ~90% | No |
| **SSH to 2nd PC + WSL** | Medium | 100% | Yes |
| **VirtualBox / Hyper-V** | Medium | 100% | No |
| **Docker (Dev Containers)** | Medium | Partial | No |
| **Dual Boot** | Hard | 100% | No |

---

## WSL1 vs WSL2

| Feature | WSL1 | WSL2 |
|---------|------|------|
| Architecture | Translation layer (no real kernel) | Real Linux kernel in lightweight VM |
| Linux compatibility | ~70% | ~100% |
| Docker support | No | Yes |
| Performance | Fast on Windows filesystem | Fast on Linux filesystem |
| Network | Shares Windows IP | Has its own virtual IP |

> **Bottom line:** Always use WSL2. WSL1 is outdated.

```powershell
# Set WSL2 as default
wsl --set-default-version 2

# Check installed distros
wsl --list --verbose
```

---

## WSL2 vs Ubuntu (in Microsoft Store)

These are NOT alternatives — they are two layers:

```
Windows
└── WSL2  (the ENGINE — a lightweight VM with a real Linux kernel)
    └── Ubuntu  (the DISTRO — the actual Linux OS running inside WSL2)
```

- **WSL2** = the platform/runtime
- **Ubuntu** = the Linux distribution running on top of it
- Installing Ubuntu from the Microsoft Store will auto-install WSL2 if missing

```powershell
# One command installs both WSL2 + Ubuntu
wsl --install
```

---

## VS Code Remote Options ("Open Remote Window")

When clicking the `><` button in VS Code bottom-left:

| Option | What It Does | Use Case |
|--------|-------------|----------|
| **Connect to WSL** | Opens local WSL2/Ubuntu | Linux dev on your own PC |
| **Connect to Host (SSH)** | SSH into any remote machine | 2nd PC, server, cloud |
| **Open in Container** | Docker container (requires Docker) | Isolated dev environments |
| **Connect to Tunnel** | Works over internet via GitHub auth | Access PC from anywhere |

---

## Connecting to a Remote PC via SSH

### Requirements
- **Local machine:** VS Code + Remote SSH extension
- **Remote machine:** OpenSSH Server running

### Enable SSH on the remote Windows PC
```powershell
# Install OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and enable on boot
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

### Connect from local machine
```powershell
# Test if SSH port is open
Test-NetConnection -ComputerName <remote-ip> -Port 22

# Connect via SSH
ssh username@<remote-ip>
```

### Check WSL on remote machine
```powershell
ssh admin@<remote-ip> "wsl --list --verbose"
```

---

## Real Example: Connecting to `itaymini`

- **Remote PC hostname:** `itaymini` (resolved via local DNS)
- **OS:** Windows 11 (Build 26100)
- **SSH:** OpenSSH Server was already running
- **User:** `admin` (local Windows account — not the Microsoft/email account)

> **Note:** Windows SSH login requires the **local Windows account** username,
> not your Microsoft account email address.

### WSL status found on itaymini
```
NAME              STATE     VERSION
* docker-desktop  Stopped   2
```
WSL2 is installed but only has `docker-desktop` (Docker's internal distro).
To install Ubuntu:
```powershell
wsl --install -d Ubuntu
```

---

## Optional: WSL GUI Tools (Not Required)

| Tool | Purpose |
|------|--------|
| **WSL UI** | Graphical manager for WSL distros |
| **WSL Toolbox** | GUI for start/stop/backup WSL |

Both are convenience wrappers — everything they do can be done via command line.
If you use VS Code, you don't need them.

---

## Recommended Learning Path

```
1. Install WSL2 locally         → wsl --install
2. Open in VS Code              → Remote > Connect to WSL
3. Run Python projects in Linux → works natively
4. SSH to 2nd PC                → Remote > Connect to Host
5. Try dual boot or VirtualBox  → when ready for full Linux
```
