import os
import subprocess
import shutil
import glob
from pathlib import Path
from typing import Optional

from .converter_interface import ConverterInterface

class DrawioConverter(ConverterInterface):
    supported_formats = {
        'drawio',
        'png',
        'pdf',
        'svg',
    }
    def __init__(self, input_file: str, output_dir: str, input_type: str, output_type: str):
        """
        Initialize Drawio converter.
        
        Args:
            input_file: Path to the input draw.io file
            output_dir: Directory where the converted file will be saved
            input_type: Input file format (must be 'drawio')
            output_type: Output file format (e.g., 'png', 'pdf', 'svg')
        """
        super().__init__(input_file, output_dir, input_type, output_type)
    
    def __can_convert(self) -> bool:
        """
        Check if the input file can be converted to the output format.
        
        Returns:
            True if conversion is possible, False otherwise
        """
        input_fmt = self.input_type.lower()
        output_fmt = self.output_type.lower()
        
        # Check if formats are supported
        if input_fmt not in self.supported_formats or output_fmt not in self.supported_formats:
            return False
        
        # Can only convert FROM drawio to other formats
        if input_fmt != 'drawio':
            return False
            
        # Cannot convert drawio to drawio
        if output_fmt == 'drawio':
            return False
        
        return True

    @classmethod
    def get_formats_compatible_with(cls, format_type: str) -> set:
        """
        Get the set of compatible formats for conversion.
        
        Args:
            format_type: The input format to check compatibility for.
        Returns:
            Set of compatible formats.
        """
        base_formats = super().get_formats_compatible_with(format_type)
        # Can convert FROM drawio but not TO drawio (export only)
        base_formats.discard('drawio')
        return base_formats
    
    def convert(self, overwrite: bool = True, quality: Optional[str] = None) -> list[str]:
        """
        Convert the draw.io file to the output format using drawio-export CLI.
        
        Args:
            overwrite: Whether to overwrite existing output file (default: True)
            quality: Quality setting (not used for drawio conversion)
        
        Returns:
            List containing the path to the converted output file
            
        Raises:
            FileNotFoundError: If input file doesn't exist or drawio-export not installed
            ValueError: If the conversion is not supported
            RuntimeError: If conversion fails
        """
        if not self.__can_convert():
            raise ValueError(f"Conversion from {self.input_type} to {self.output_type} is not supported.")
        
        # Check if input file exists
        if not os.path.isfile(self.input_file):
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        # Check if drawio-export is available
        if not shutil.which('drawio-export'):
            raise FileNotFoundError(
                "drawio-export CLI tool not found. "
                "Please install it with: npm install -g @mattiash/drawio-export"
            )
        
        # Generate output filename
        input_filename = Path(self.input_file).stem
        output_file = os.path.join(self.output_dir, f"{input_filename}.{self.output_type}")
        
        # Check if output file exists and overwrite is False
        if not overwrite and os.path.exists(output_file):
            return [output_file]
        
        try:
            # Ensure output_dir has a trailing slash for drawio-export
            output_dir_normalized = self.output_dir.rstrip('/') + '/'
            
            # Build the drawio-export command
            cmd = [
                'drawio-export',
                '-f', self.output_type,
                '-o', output_dir_normalized,
            ]
            
            # Add transparency for PNG format
            if self.output_type.lower() == 'png':
                cmd.append('-t')
            
            # Add input file at the end
            cmd.append(self.input_file)
            
            # Run the conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Find the generated file(s) - drawio-export creates files like "Page-1.png"
            # They will be in output_dir with pattern Page-*.{output_type}
            pattern = os.path.join(self.output_dir, f"Page-*.{self.output_type}")
            generated_files = glob.glob(pattern)
            
            if not generated_files:
                # Try alternative patterns
                alt_patterns = [
                    os.path.join(self.output_dir, f"*Page-*.{self.output_type}"),
                    os.path.join(self.output_dir, f"*.{self.output_type}"),
                ]
                for alt_pattern in alt_patterns:
                    generated_files = glob.glob(alt_pattern)
                    if generated_files:
                        break
            
            if not generated_files:
                # List directory contents for debugging
                dir_contents = os.listdir(self.output_dir) if os.path.exists(self.output_dir) else []
                raise RuntimeError(
                    f"No output file was created. Expected pattern: {pattern}\n"
                    f"Directory contents: {dir_contents}\n"
                    f"Command: {' '.join(cmd)}\n"
                    f"Stdout: {result.stdout}\n"
                    f"Stderr: {result.stderr}"
                )
            
            # Use the first generated file (usually there's only one page)
            generated_file = generated_files[0]
            
            # Move/rename to the expected output filename
            if generated_file != output_file:
                shutil.move(generated_file, output_file)
            
            return [output_file]
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Drawio conversion failed: {e.stderr or e.stdout or str(e)}"
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Drawio conversion failed: {str(e)}"
            raise RuntimeError(error_msg)
