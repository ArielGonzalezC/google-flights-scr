import os
import subprocess
from setuptools import setup
from setuptools.command.build_py import build_py


class BuildPyCommand(build_py):
    """Custom build command to compile protobuf files."""
    
    def run(self):
        # Try to compile protobuf files if protoc is available
        proto_files = [
            'fast_flights/schema_roundtrip.proto',
        ]
        
        for proto_file in proto_files:
            if os.path.exists(proto_file):
                try:
                    # Check if protoc is available
                    subprocess.run(['protoc', '--version'], 
                                 capture_output=True, check=True)
                    
                    # Compile the proto file
                    proto_dir = os.path.dirname(proto_file)
                    subprocess.run([
                        'protoc',
                        f'--python_out={proto_dir}',
                        proto_file
                    ], check=True)
                    print(f"Successfully compiled {proto_file}")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print(f"Warning: protoc not found or failed to compile {proto_file}")
                    print("Skipping protobuf compilation. The package may not work correctly.")
        
        # Continue with normal build
        build_py.run(self)


if __name__ == "__main__":
    setup(
        cmdclass={
            'build_py': BuildPyCommand,
        },
        package_data={
            'fast_flights': ['*.proto', '*.pyi', 'py.typed'],
        },
    )

# testing
