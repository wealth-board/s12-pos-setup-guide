# Hosting the POS database remotely

By default the [main guide](../README.md) installs SQL Server on the till laptop itself. This page covers putting the database on a **different machine**, so that:

- several tills (and the PP4 handheld app) share the same products, stock and sales
- the data survives if a till laptop breaks or is stolen
- the database can run on Linux (see [linux-wine.md](linux-wine.md))

## Choose a setup

| Setup | Best for | Internet needed for sales? |
|---|---|---|
| **A. Shop server on the local network** (Windows or Linux) | One shop, several tills | ❌ No |
| **B. Cloud server + VPN** | Several shops sharing data, head-office access | ✅ Yes |
| **C. Managed cloud database** (Azure SQL etc.) | Not recommended | ✅ Yes |

**Recommendation:** use **A** for a single shop. A till that depends on the internet stops selling when the connection drops. Use **B** only if several shops really need to share data in real time.

---

## Setup A: a database server in the shop

One computer in the shop runs SQL Server. It must be **always on** and connected by **network cable** (not Wi-Fi). Every till connects to it over the shop network.

### A1. Windows server

1. On the server, do Steps 1, 3, 4 and 5 of the [main guide](../README.md): install SQL Server Express, enable `sa`, enable TCP/IP on port 1433, restart.
2. Give the server a **fixed IP address**, e.g. `192.168.1.10`. Either reserve it in the router's DHCP settings (best) or set it in Windows network settings.
3. Allow port 1433 through Windows Firewall. Run this in an **administrator** Command Prompt:
   ```
   netsh advfirewall firewall add rule name="SQL Server 1433" dir=in action=allow protocol=TCP localport=1433 profile=private
   ```
   Make sure the shop network is set to **Private** in Windows (Settings → Network → Properties).
4. Stop Windows from sleeping: Settings → System → Power → Sleep: **Never**.

### A2. Linux server (Docker)

SQL Server 2022 runs natively on Linux. Docker is the simplest way to run it:

```bash
# Install Docker first: https://docs.docker.com/engine/install/
sudo docker run -d --name pos-sql \
  -e ACCEPT_EULA=Y \
  -e MSSQL_PID=Express \
  -e 'MSSQL_SA_PASSWORD=YourStrongPassword1!' \
  -p 1433:1433 \
  -v pos-sql-data:/var/opt/mssql \
  --restart unless-stopped \
  mcr.microsoft.com/mssql/server:2022-latest
```

- `MSSQL_PID=Express` uses the free Express edition, the same as on Windows.
- `-v pos-sql-data:…` keeps the database files in a Docker volume, so they survive container restarts and upgrades.
- `--restart unless-stopped` starts SQL Server again after a reboot.

Check that it's running:

```bash
sudo docker exec -it pos-sql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword1!' -C -Q "SELECT @@VERSION"
```

Then give the server a fixed IP, as in A1 step 2. If the Linux firewall is on, open the port: `sudo ufw allow from 192.168.1.0/24 to any port 1433 proto tcp`.

> If you'd rather not use Docker, Microsoft also has native packages for Ubuntu and RHEL. Search for "Install SQL Server 2022 on Linux". After installing, run `sudo /opt/mssql/bin/mssql-conf setup` and choose Express.

### A3. Connect each till

On each till: POS login window → **Setting** → **Database Setting**:

| Field | Value |
|---|---|
| Main Address | `192.168.1.10` (the server's IP; on Windows, `192.168.1.10\SQLEXPRESS` also works if SQL Server Browser is running) |
| Port | `1433` |
| User Name / Password | `sa` / server password |
| Database Name | `POS` (the same on every till) |

Click **Server Connection Test** and then **Database Test**. Then bind each till to its **own** terminal number (`01`, `02`, `03`…), as in [Step 7](../README.md#step-7-bind-this-laptop-as-a-till-terminal) of the main guide.

> Only one till needs to create the database or run the setup wizard. The others connect to the existing `POS` database.

---

## Setup B: cloud server and VPN

Run SQL Server on a cloud VM (DigitalOcean, Hetzner, AWS Lightsail, Azure VM, etc.), using the Docker command from A2, and connect the tills to it **through a VPN**.

> ⚠️ **Never open port 1433 to the whole internet.** Internet-exposed SQL Servers get scanned and password-guessed around the clock. Always put a VPN between the tills and the server.

### B1. Tailscale (simplest VPN)

[Tailscale](https://tailscale.com/) builds a private network between your devices, and the free plan is enough for a small shop.

1. Install Tailscale on the **server** and on **every till**, all signed in to the same account.
2. Find the server's Tailscale IP: run `tailscale ip -4` on the server. It looks like `100.x.y.z`.
3. Make Docker listen **only** on the Tailscale IP, not on the public internet:
   ```bash
   -p 100.x.y.z:1433:1433      # instead of -p 1433:1433
   ```
4. Block 1433 on the server's public interface as well, in the cloud provider's firewall or security group.
5. In each till's **Database Setting**, set Main Address to `100.x.y.z`.

WireGuard or a router-to-router VPN also work. Tailscale just needs the least setup.

### B2. Downsides to plan for

- **Internet outages stop sales.** The POS login has an **Offline** checkbox and a **Second Address** field, which may provide a fallback. Test how they behave before relying on them. Get a backup connection (e.g. a 4G router).
- **Speed:** every scan and sale goes over the internet, so choose a server region close to the shop.
- **Cost:** a 2 GB RAM VM is the practical minimum for SQL Server (about $10–20 a month).

---

## Setup C: managed cloud databases (not recommended)

Services such as **Azure SQL Database** and **AWS RDS for SQL Server** look easy, but:

- Azure SQL Database **can't restore a `.bak` file** directly. Azure SQL Managed Instance can, but it costs much more.
- The POS's "New Database", "Attach/Detach" and "Restore" buttons assume full control of a normal SQL Server and probably won't work.
- They're expensive for a shop-sized database.

A VM running SQL Server (Setup B) is cheaper and behaves exactly like the in-shop server.

---

## Moving an existing database to the server

1. **Back it up** on the old machine, either with the POS backup or in SQLCMD:
   ```sql
   BACKUP DATABASE POS TO DISK = 'C:\Program Files\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQL\Backup\POS-move.bak'
   GO
   ```
2. **Copy** the `.bak` file to the server.
3. **Restore** it on the server.
   - Windows: follow [Restoring old data](../README.md#optional-restoring-old-data) in the main guide.
   - Linux/Docker: first list the logical file names inside the backup:
     ```bash
     sudo docker cp POS-move.bak pos-sql:/var/opt/mssql/backup.bak
     sudo docker exec -it pos-sql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword1!' -C \
       -Q "RESTORE FILELISTONLY FROM DISK='/var/opt/mssql/backup.bak'"
     ```
     Then restore it, using those logical names. For `POS2026.bak` they're `InitDB` and `InitDB_log`:
     ```bash
     sudo docker exec -it pos-sql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword1!' -C -Q "
       RESTORE DATABASE POS FROM DISK='/var/opt/mssql/backup.bak'
       WITH MOVE 'InitDB' TO '/var/opt/mssql/data/POS.mdf',
            MOVE 'InitDB_log' TO '/var/opt/mssql/data/POS_log.ldf', REPLACE"
     ```
4. Point every till at the server (see [A3](#a3-connect-each-till)).

> If you see collation-conflict errors after moving a database, the server's default collation differs from the database's. Run `SELECT DATABASEPROPERTYEX('POS','Collation')` to see the database's collation. On Docker, recreate the container with `-e MSSQL_COLLATION=<that collation>`, then restore again.

---

## Backups on a database server

SQL Server **Express has no SQL Agent**, so it can't schedule its own backups. The POS's built-in backup ([Step 8](../README.md#step-8-initial-setup-wizard-tax-and-backups)) runs on the server, so its **Backup Path is most likely a folder on the server**, not on the till.

To make sure backups happen whatever the POS does:

**Linux (cron):** a daily backup at 23:30 that keeps 14 days:

```bash
sudo mkdir -p /srv/pos-backups
# crontab -e   (as root)
30 23 * * * docker exec pos-sql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword1!' -C -Q "BACKUP DATABASE POS TO DISK='/var/opt/mssql/backup/POS-$(date +\%F).bak' WITH INIT" && docker cp pos-sql:/var/opt/mssql/backup/. /srv/pos-backups/ && find /srv/pos-backups -name '*.bak' -mtime +14 -delete
```

(Create the folder inside the container once: `sudo docker exec pos-sql mkdir -p /var/opt/mssql/backup`.)

**Windows (Task Scheduler):** create a daily task that runs:

```
sqlcmd -S .\SQLEXPRESS -E -Q "BACKUP DATABASE POS TO DISK='C:\Program Files\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQL\Backup\POS-daily.bak' WITH INIT"
```

**Either way, copy backups off the server** (cloud storage, USB drive, or another machine), and **test a restore** now and then.

---

## Security checklist

- [ ] Strong `sa` password, different from any password used elsewhere
- [ ] Port 1433 is open **only** to the shop network or the VPN, never to the internet
- [ ] Server has a fixed IP address
- [ ] Automatic daily backups, with copies kept somewhere else
- [ ] OS and SQL Server updates installed regularly (Docker: `docker pull mcr.microsoft.com/mssql/server:2022-latest`, then recreate the container; the volume keeps the data)
- [ ] Optional: a dedicated SQL login for the POS instead of `sa`. This hasn't been tested with this POS, and the "New Database" and "Restore" buttons need extra server permissions.

## SQL Server Express limits

Express is free but limited to **10 GB per database**, 4 CPU cores and about 1.4 GB of RAM for its cache. A shop's POS database (the sample backup is 27 MB) stays far below that for years.
