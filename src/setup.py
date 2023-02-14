from cx_Freeze import setup, Executable

packages = ["torch", "whisper"]
file_include = ["config.json"]

build_exe_options = {"packages": packages, "include_files": file_include}
setup(
    name="OBSWSTT",
    version="0.1",
    description="OBSWSTT",
    options={"build_exe": build_exe_options},
    executables=[Executable("OBSWSTT.py", targetName="OBSWSTT.exe", base=False)],
)
