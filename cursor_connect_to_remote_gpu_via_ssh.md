# Connect to remote GPU via SSH
_Exported on 12/7/2025 at 19:57:40 EST from Cursor (2.1.50)_

---

**User**

I need to connect to a GPU for a new project, here is a guide I got from Claude :"Looking at your screenshots, you've deployed a GPU instance with SSH access enabled. To connect Cursor to this remote GPU, you'll need to use Remote - SSH. Here's how:

Step 1: Get Your SSH Connection Details

Click "Show Details" on your running instance (or "Manage" next to SSH Access in the configuration). You'll need:

Host/IP address

SSH Port (often not the standard 22)

Username (likely jovyan or root based on your init script)

SSH Key or Password

Step 2: Set Up SSH in Cursor

Open Cursor → Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)

Type "Remote-SSH: Connect to Host" and select it

Click "+ Add New SSH Host"

Enter your connection string:

   ssh jovyan@<YOUR_HOST_IP> -p <SSH_PORT>

Save to your SSH config file when prompted

Step 3: Configure SSH Key (if required)

If the service provides an SSH key, save it locally and update your ~/.ssh/config:

Host gpu-server

    HostName <YOUR_HOST_IP>

    User jovyan

    Port <SSH_PORT>

    IdentityFile ~/.ssh/your_private_key

    StrictHostKeyChecking no

Then connect using the host alias gpu-server.

Step 4: Connect and Open Your Project

Use "Remote-SSH: Connect to Host" again

Select your configured host

Once connected, use File → Open Folder to navigate to your project directory (likely /home/jovyan/ or your mounted storage volume Emma_Storage)

"   Here is the GPU details: Jupyter 16G Pytorch

Running • 13 mins 41 seconds

$0.46

$2.00/hr

Template:

Jupyter 16G Pytorch

Created By:

popoxu215@hotmail.com

Created On:

December 07, 2025 **SSH Access**

ssh [jovyan@64.247.206.5](mailto:jovyan@64.247.206.5) -p 32137

**HTTP Ports:**

[https://jupyter-labs-8888-1765153957039629177.cluster3.service-inference.ai?token=O84Kc5y9G13v7WI2](https://jupyter-labs-8888-1765153957039629177.cluster3.service-inference.ai/?token=O84Kc5y9G13v7WI2), Please guide me step by step on how to connect to this GPU. I have install Remote-SSH and updated SSH Access into the config file.

---

**Cursor**

好的！我来帮你一步步连接到这个GPU服务器。你已经安装了Remote-SSH并更新了配置文件，让我先检查一下你的SSH配置是否正确。

```plaintext
Host gpu-server
    HostName 64.247.206.5
    User jovyan
    Port 32137
    IdentityFile ~/.ssh/your_private_key  # 如果需要密钥
    StrictHostKeyChecking no
```

我看到你的SSH配置文件格式不太正确。当前只是一个命令，而不是正确的配置格式。让我帮你修正它：

```plaintext
Host gpu-server
    HostName 64.247.206.5
    User jovyan
    Port 32137
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

```

很好！SSH配置文件已经修正。现在让我测试一下SSH连接：

🎉 **太棒了！SSH连接测试成功！** 不需要密钥就能直接连接。

现在按照以下步骤在Cursor中连接到GPU服务器：

---

## 📋 连接步骤

### 第1步：打开Remote-SSH连接
1. 按 **`Cmd + Shift + P`** 打开命令面板
2. 输入 **"Remote-SSH: Connect to Host"** 并选择它

### 第2步：选择主机
在弹出的列表中，你应该能看到 **`gpu-server`** 这个选项，点击它

### 第3步：等待连接
- Cursor会在新窗口中打开
- 左下角会显示连接状态，等待变成 **"SSH: gpu-server"** 表示连接成功

### 第4步：打开项目文件夹
连接成功后：
1. 点击 **File → Open Folder**
2. 导航到 **`/home/jovyan/work`**（这是你的持久存储挂载路径 `Emma_Storage`）
3. 点击 **OK** 打开

---

## 📌 重要路径说明

| 路径 | 说明 |
|------|------|
| `/home/jovyan/` | 用户主目录 |
| `/home/jovyan/work` | **Emma_Storage** (50GB持久存储，重启不会丢失) |

---

**你现在可以按 `Cmd + Shift + P` 开始连接了！** 如果遇到任何问题请告诉我。

请告诉我你的下一步进展或任何问题！

