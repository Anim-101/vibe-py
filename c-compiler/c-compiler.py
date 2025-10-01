import subprocess
import sys
import os

def compile_c_file(source_file, output_file=None):
    if not os.path.isfile(source_file):
        print(f"Source file '{source_file}' does not exist.")
        return False

    if output_file is None:
        output_file = os.path.splitext(source_file)[0]

    compile_cmd = ["gcc", source_file, "-o", output_file]
    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Compilation successful. Output: {output_file}")
            return True
        else:
            print("Compilation failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error during compilation: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python c-compiler.py <source_file.c> [output_file]")
        sys.exit(1)
    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    compile_c_file(source, output)