# TypeScript to Python Conversion Tool

This tool provides an automated way to convert a TypeScript project to Python for Steam release. The conversion process is designed to be as accurate as possible, but manual adjustments might be necessary for complex TypeScript features.

## Overview

The conversion process consists of three main steps:

1. **Convert TypeScript files to Python** using the `ts2py.py` script
2. **Fix common issues** in the converted files using the `fix_python_conversion.py` script
3. **Create a complete Python project** with the `convert_project.py` script

## Requirements

- Python 3.8 or higher
- `autopep8` package (`pip install autopep8`)

## Usage

### Quick Start

For a complete conversion with one command:

```bash
python convert_project.py ./src --output-dir ./python_converted
```

This will:
1. Convert all TypeScript files to Python
2. Copy non-TypeScript files
3. Create `__init__.py` files to make proper Python packages
4. Fix common issues in the converted Python files
5. Create a `requirements.txt` file with Python equivalents of npm packages
6. Create a `README.md` file for the converted project
7. Create an `app.py` entry point

### Step-by-Step Conversion

If you prefer to run each step manually:

#### 1. Convert a single TypeScript file:

```bash
python ts2py.py path/to/file.ts --output path/to/output.py
```

#### 2. Convert all TypeScript files in a directory:

```bash
python ts2py.py path/to/src_dir --output path/to/output_dir --recursive
```

#### 3. Fix common issues in converted Python files:

```bash
python fix_python_conversion.py path/to/output_dir --recursive
```

#### 4. Complete project conversion:

```bash
python convert_project.py path/to/src_dir --output-dir path/to/output_dir
```

## Customization

The conversion process can be customized by modifying the scripts:

- `ts2py.py`: Edit the `TYPE_MAPPING` and `IMPORT_MAPPING` dictionaries to change how TypeScript types and imports are converted
- `fix_python_conversion.py`: Add new fixers to the `PythonFixer` class
- `convert_project.py`: Modify the `IGNORE_EXTENSIONS` and `IGNORE_DIRS` lists to change which files are copied

## Known Limitations

- TypeScript decorators are not fully supported
- React components need significant reworking for Flask/Python environment
- Complex TypeScript types may not convert perfectly
- Some JavaScript/TypeScript idioms don't translate directly to Python
- Jest tests need manual conversion to pytest format

## Post-Conversion Steps

After conversion, you'll likely need to:

1. Install Python dependencies: `pip install -r requirements.txt`
2. Manually adjust complex TypeScript features that didn't convert properly
3. Set up a proper Flask application structure if using web components
4. Create Steam integration using Python libraries
5. Update asset paths and file handling for Steam environment

## Converting React UI to Python

For React components, you have several options:

1. **Use Flask with Jinja2 templates**: Rewrite React components as server-rendered templates
2. **Use a Python GUI framework**: Tkinter, PyQt, wxPython, or PyGame for desktop applications
3. **Use a web view in Steam**: Run a local web server with Flask and display in Steam's browser
4. **Use the Steam Overlay**: Create a minimal HTML/CSS/JS frontend displayed in the Steam overlay

The most direct approach for Steam is using PyGame or a similar Python GUI framework.

## Troubleshooting

- **Import errors**: Check that all imports have been properly converted and Python module structure is correct
- **Syntax errors**: Some complex TypeScript features may need manual conversion
- **Missing dependencies**: Ensure all required Python packages are installed
- **Type errors**: Python's type system is less strict than TypeScript's, so some type checking is lost

## License

This conversion tool is provided under the MIT License. 