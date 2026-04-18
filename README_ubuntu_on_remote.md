# Ubuntu on Remote Windows PC — How It Was Done

## Goal
Run a real Ubuntu Linux environment on a remote Windows 11 PC (`itaymini`, IP: `10.100.102.11`)
without a separate physical Linux machine, accessible via SSH from anywhere.

---

## The Method: WSL2 (Windows Subsystem for Linux)

**WSL2** is a feature built into Windows 10/11 that lets you run a real Linux kernel
inside Windows — not a virtual machine, not an emulator.  
You get a full Ubuntu terminal, `apt`, Python, bash — everything.

**Why WSL2 and not Docker?**
- Docker Desktop on itaymini was broken (required GUI to fix its WSL backend error)
- WSL2 is lighter, simpler, and feels more like "real Linux" for learning

**The challenge:**  
WSL2 normally requires a desktop (GUI) session to initialize.  
**Solution:** We used physical access once to run the import command, then everything else was done remotely via SSH.

---

## Machine Details

| Property | Value |
|---|---|
| Hostname | itaymini |
| IP Address | 10.100.102.11 |
| OS | Windows 11 |
| Windows user | admin |
| Ubuntu location | `E:\WSL\Ubuntu\` |
| Ubuntu version | 22.04.4 LTS (Jammy Jellyfish) |

---

## Step-by-Step: What Was Done

### Step 1 — Prepare the Ubuntu rootfs
We already had an Ubuntu 22.04 root filesystem archive downloaded at:
```
C:\Windows\Temp\ubuntu-rootfs.tar.gz  (234 MB)
```
This is the base Ubuntu filesystem — like a compressed copy of a fresh Ubuntu install.

### Step 2 — Create folder on E drive (via SSH)
```cmd
ssh admin@10.100.102.11 "mkdir E:\WSL\Ubuntu"
```
This is where Ubuntu's virtual disk will live.

### Step 3 — Import Ubuntu into WSL (PHYSICAL ACCESS REQUIRED — once only)
On itaymini, open **PowerShell as Administrator** and run:
```powershell
wsl --import Ubuntu E:\WSL\Ubuntu C:\Windows\Temp\ubuntu-rootfs.tar.gz --version 2
```
- `Ubuntu` = name of the distro
- `E:\WSL\Ubuntu` = where to store the virtual disk (ext4.vhdx file)
- `--version 2` = use WSL2 (modern kernel, faster)

If a distro with that name already exists:
```powershell
wsl --unregister Ubuntu   # deletes the old one
wsl --import Ubuntu ...   # then re-import
```

### Step 4 — Install packages inside Ubuntu (via SSH)
```cmd
ssh admin@10.100.102.11 "wsl -d Ubuntu -u root -e apt-get update -qq"
ssh admin@10.100.102.11 "wsl -d Ubuntu -u root -e apt-get install -y openssh-server python3 python3-pip"
```
- `-d Ubuntu` = use the Ubuntu distro specifically (important if Docker WSL is also present)
- `-u root` = run as root user
- Installs: SSH server, Python 3, pip

### Step 5 — Create user and configure SSH
We wrote a bash script (`setup_wsl.sh`) and ran it inside Ubuntu:

**`setup_wsl.sh`:**
```bash
#!/bin/bash
echo itay:itay123 | /usr/sbin/chpasswd          # set password for user 'itay'
echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config  # allow password login
/usr/sbin/service ssh start                      # start SSH server
echo DONE
```

Run it via SSH:
```cmd
scp setup_wsl.sh admin@10.100.102.11:C:\Windows\Temp\setup_wsl.sh
ssh admin@10.100.102.11 "wsl -d Ubuntu -u root -- /bin/bash /mnt/c/Windows/Temp/setup_wsl.sh"
```
> **Note:** Inside WSL, Windows drives are mounted at `/mnt/`. So `C:\` = `/mnt/c/`, `E:\` = `/mnt/e/`

Also create the Linux user (done separately):
```cmd
ssh admin@10.100.102.11 "wsl -d Ubuntu -u root -- /usr/sbin/useradd -m -s /bin/bash -G sudo itay"
```
- `-m` = create home directory `/home/itay`
- `-s /bin/bash` = use bash shell
- `-G sudo` = add to sudo group (admin)

### Step 6 — Port Forwarding (why it's needed)
WSL2 runs in its own private network inside Windows. Ubuntu gets an internal IP like `172.23.3.167` — **not reachable from outside Windows**.

To allow SSH from outside, we forward Windows port `2222` → Ubuntu port `22`:
```cmd
ssh admin@10.100.102.11 "netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=22 connectaddress=172.23.3.167"
```
Also open the firewall:
```cmd
ssh admin@10.100.102.11 "netsh advfirewall firewall add rule name=WSL_Ubuntu_SSH dir=in action=allow protocol=TCP localport=2222"
```

**The problem:** WSL2 IP changes every reboot. The auto-start script handles this automatically.

### Step 7 — Auto-Start Script
**`wsl_autostart.ps1`** — runs on every Windows boot:
```powershell
# Start SSH inside Ubuntu WSL
wsl -d Ubuntu -u root -- /usr/sbin/service ssh start

# Get current WSL IP (changes every reboot)
$wslIp = (wsl -d Ubuntu -u root -- ip addr show eth0) |
    Select-String 'inet ' |
    ForEach-Object { $_.ToString().Trim().Split(' ')[1].Split('/')[0] }

if ($wslIp) {
    # Update port proxy with new IP
    netsh interface portproxy delete v4tov4 listenport=2222 listenaddress=0.0.0.0
    netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=22 connectaddress=$wslIp
    Write-Output "WSL Ubuntu SSH started. IP: $wslIp, forwarded on port 2222"
}
```

### Step 8 — Register as Windows Scheduled Task
**`register_task.ps1`** — registers the auto-start script to run at every Windows boot:
```powershell
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File C:\Windows\Temp\wsl_autostart.ps1"

$trigger  = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
$principal = New-ScheduledTaskPrincipal -UserId "admin" -RunLevel Highest -LogonType Interactive

Register-ScheduledTask -TaskName "WSL_Ubuntu_AutoStart" `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
```

Run once to register:
```cmd
ssh admin@10.100.102.11 "powershell -ExecutionPolicy Bypass -File C:\Windows\Temp\register_task.ps1"
```

To manually trigger it anytime:
```cmd
ssh admin@10.100.102.11 "schtasks /run /tn WSL_Ubuntu_AutoStart"
```

---

## How to Connect

### SSH into Ubuntu from anywhere:
```bash
ssh itay@10.100.102.11 -p 2222
```

| | |
|---|---|
| Host | 10.100.102.11 |
| Port | 2222 |
| Username | itay |
| Password | itay123 |

> **Change your password** after first login:
> ```bash
> passwd
> ```

### Run a single command without opening a shell:
```bash
ssh -p 2222 itay@10.100.102.11 "python3 --version"
```

---

## Port Map Summary

| Port | On | Direction | Purpose |
|---|---|---|---|
| 22 | Windows (itaymini) | inbound | SSH to Windows admin |
| 2222 | Windows (itaymini) | inbound → forwarded | SSH to Ubuntu WSL |
| 22 | Ubuntu WSL (internal) | internal only | SSH server inside Ubuntu |

---

## Final Status

| Component | Status | Details |
|---|---|---|
| Ubuntu version | ✅ Running | 22.04.4 LTS (Jammy Jellyfish) |
| Location | ✅ E drive | `E:\WSL\Ubuntu\` |
| SSH access | ✅ Working | port 2222 |
| Python | ✅ Installed | Python 3.10.12 |
| pip | ✅ Installed | ready for packages |
| Auto-start on boot | ✅ Active | Scheduled Task: `WSL_Ubuntu_AutoStart` |
| Linux user | ✅ Created | `itay` with sudo |

---

## Useful Commands

```bash
# Inside Ubuntu — check you have sudo
sudo apt update

# Install any package
sudo apt install -y nano git curl

# Install Python packages
pip3 install paho-mqtt

# Check IP inside Ubuntu
ip addr show eth0
```

```cmd
# From your PC — check WSL is running on itaymini
ssh admin@10.100.102.11 "wsl -d Ubuntu -u root -- /usr/sbin/service ssh status"

# Manually start if needed
ssh admin@10.100.102.11 "schtasks /run /tn WSL_Ubuntu_AutoStart"
```
