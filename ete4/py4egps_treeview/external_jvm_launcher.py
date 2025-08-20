import platform
import subprocess
import json
from pathlib import Path
from typing import Sequence, Optional, List
from ete4 import Tree

"""
The JVM launcher configuration:
{config_egps_file}
The path is same as Py4eGPS package, so, user do not need to configurator again.
"""

config_file_default_template = """
# The blank area of top,left,bottom,right .
$blank.space=20,20,80,80
# Whether display the leaf label on the tree.
$show.leaf.label=T
""".splitlines()

config_egps_file = Path.home() / '.eGPS4Py' / 'egps_config.json'



def configure_egps(egps_software_path: str):
    """
    Configure JVM paths and save to user directory to avoid permission issues.

    Args:
        egps_software_path (str): Path to eGPS software path
    """
    path_installed = Path(egps_software_path)
    path_java_bin = path_installed / "jre" / "bin" / "java"
    data = {'egps_software_path': path_installed.resolve().as_posix(), 'java_bin': path_java_bin.resolve().as_posix()}
    # Save configuration to user home directory to avoid permission issues
    config_dir = Path.home() / '.eGPS4Py'
    config_dir.mkdir(exist_ok=True)
    with open(config_egps_file, 'w') as f:
        json.dump(data, f)


def get_user_egps_configure():
    """
    Get user-specific eGPS configuration from home directory.

    Returns:
        tuple: A tuple containing (java_vm_path, java_class_path)

    Raises:
        FileNotFoundError: If user configuration file does not exist
    """
    # Read configuration from user directory
    if config_egps_file.exists():
        with open(config_egps_file, 'r') as f:
            loaded_data = json.load(f)
        return loaded_data['egps_software_path'], loaded_data['java_bin']
    else:
        # If user configuration does not exist, raise exception
        raise FileNotFoundError("JVM configuration not found. Please call configure_jvm() first.")
def launch_egps_treeview(
    tree: Tree,
    jvm_opts: Optional[Sequence[str]] = None,
    log_file_name: str = "egps.log.file",
    config_templete: Optional[Sequence[str]] = None,
    extra_configs: Optional[Sequence[str]] = None,

) -> subprocess.Popen:
    """
    Start a Swing-based JAR and return the Popen handle.

    Parameters
    ----------
    tree: Tree
        The ete4 tree instance
    jvm_opts : list[str] | None
        Extra JVM flags, e.g. ["-Xmx2G", "-Dmy.prop=value"].
    """

    if not config_egps_file.exists():
        raise FileNotFoundError(f"Please configure eGPS software path first, use configure_egps()")
    egps_installed_path,java_bin = get_user_egps_configure()
    if config_templete:
        config_file_template_suffix = config_templete
    else:
        config_file_template_suffix = config_file_default_template

    output_config_list = []
    if extra_configs:
        output_config_list.append(extra_configs)


    cmd = [java_bin,"-cp", "./eGPS_lib/*;.","@eGPS2.args","-splash:./laucher.gif","-Xss2m","-Xms7g","-Xmx8g"]
    if jvm_opts:
        cmd += list(jvm_opts)

    tmp_config_file = Path("temp.egps.modern.tree.view.txt")
    path_of_config = tmp_config_file.resolve().as_posix()

    cmd += ["api.rpython.ModernTreeViewPyLauncher", path_of_config]
    # cmd = ["python", "-c", "import os, sys; print(os.getcwd())"] # test for the cwd
    print(f"[RUN CMD:] {cmd}")
    # ② 处理日志
    log_file = open(log_file_name, "a")
    stdout = log_file
    stderr = log_file

    # ③ 跨平台独立 / 进程组设置
    system = platform.system()
    creationflags = 0
    preexec_fn = None

    proc = subprocess.Popen(
        cmd,
        cwd = egps_installed_path,
        stdout=stdout,
        stderr=stderr,
        creationflags=creationflags,
        preexec_fn=preexec_fn,
        text=True,
    )
    tmp_tree_file = Path("temp.tree.nwk")

    tree.write(outfile=tmp_tree_file)
    output_config_list.append(f"$input.nwk.path={tmp_tree_file.resolve().as_posix()}")
    output_config_list.extend(config_file_template_suffix)

    tmp_config_file.write_text("\n".join(output_config_list))

    print(f"[INFO] GUI launched (pid={proc.pid})")
    return proc

