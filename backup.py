import contextlib
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, List
from zipfile import ZipFile
from zlib import Z_DEFAULT_COMPRESSION

from paramiko import SSHClient, SFTPClient


# Add your settings here:
SSH_HOST = "some.server.com"
SSH_PORT = 22
USERNAME = "ssh username"
IDENTITY = "/path/to/identity/file"
REMOTE_BACKUP_DIR = Path("/remote/backup/dir")

BACKUP_FILES = [
    "/some/dur",
    "/some/file.txt",
]
BACKUP_PATHS: List[Path] = list(map(lambda x: Path(x), BACKUP_FILES))


def timestamp() -> str:
    return datetime.now().strftime("%Y.%m.%d_%H:%M:%S")


def log(msg: str) -> None:
    print(f"{timestamp()} {msg}")


@contextlib.contextmanager
def setup_ssh() -> Tuple[SSHClient, SFTPClient]:
    ssh: Optional[SSHClient] = None
    sftp: Optional[SFTPClient] = None
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        log(f"Connecting to {SSH_HOST}:{SSH_PORT} as {USERNAME} using {IDENTITY}")
        ssh.connect(SSH_HOST, port=SSH_PORT, username=USERNAME, key_filename=IDENTITY)
        sftp = ssh.open_sftp()
        log("Connected")
        yield ssh, sftp
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()


def send_file(sftp: SFTPClient, src_path: Path, dest_path: Path) -> None:
    log(f"Sending file {src_path} to {dest_path}")
    sftp.put(str(src_path), str(dest_path / src_path.name), confirm=True)


@contextlib.contextmanager
def create_backup() -> Path:
    tmp_file = Path(f"/tmp/backup-{timestamp()}.zip")
    log(f"Creating backup zip")
    try:
        with ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED, compresslevel=Z_DEFAULT_COMPRESSION) as zip_file:
            for path in BACKUP_PATHS:
                zip_r(zip_file, path)
            zip_file.close()
            yield tmp_file
    finally:
        if tmp_file.exists() and tmp_file.is_file():
            Path.unlink(tmp_file)


def zip_r(zip_file: ZipFile, path: Path):
    if path.is_file():
        print(f"    - Adding {path}")
        zip_file.write(path)
    elif path.is_dir():
        print(f"    Entering {path}")
        for child in path.iterdir():
            zip_r(zip_file, child)


def main():
    log(f"Starting backup")
    with setup_ssh() as client, create_backup() as backup_file:
        sftp: SFTPClient = client[1]
        send_file(sftp, backup_file, REMOTE_BACKUP_DIR)
    log(f"Done with backup")


main()
