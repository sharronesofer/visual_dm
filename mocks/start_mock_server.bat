@echo off
REM Visual DM Mock Server Startup Script (Windows)
REM ===============================================

setlocal enabledelayedexpansion

REM Configuration
set DEFAULT_HOST=localhost
set DEFAULT_PORT=3001
set DEFAULT_DEBUG=false
set SCRIPT_DIR=%~dp0

REM Initialize variables
set HOST=%DEFAULT_HOST%
set PORT=%DEFAULT_PORT%
set DEBUG=%DEFAULT_DEBUG%
set INSTALL_DEPS_ONLY=false
set GENERATE_FIXTURES_ONLY=false

REM Colors (if supported)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Function to print status messages
goto :parse_args

:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Function to check if port is available
:check_port
netstat -an | find ":%~1 " | find "LISTENING" >nul
if %errorlevel% equ 0 (
    exit /b 1
) else (
    exit /b 0
)

REM Function to install dependencies
:install_dependencies
call :print_status "Checking dependencies..."

where python >nul 2>nul
if %errorlevel% neq 0 (
    where python3 >nul 2>nul
    if %errorlevel% neq 0 (
        call :print_error "Python 3 is required but not installed."
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

if not exist "%SCRIPT_DIR%requirements.txt" (
    call :print_error "requirements.txt not found in %SCRIPT_DIR%"
    exit /b 1
)

call :print_status "Installing Python dependencies..."
%PYTHON_CMD% -m pip install -r "%SCRIPT_DIR%requirements.txt"

if %errorlevel% equ 0 (
    call :print_success "Dependencies installed successfully"
) else (
    call :print_error "Failed to install dependencies"
    exit /b 1
)
goto :eof

REM Function to generate fixtures if needed
:generate_fixtures
call :print_status "Checking fixtures..."

if not exist "%SCRIPT_DIR%character" (
    call :print_warning "Fixtures not found. Generating..."
    goto :do_generate
)
if not exist "%SCRIPT_DIR%npc" (
    call :print_warning "Fixtures not found. Generating..."
    goto :do_generate
)

call :print_success "Fixtures already exist"
goto :eof

:do_generate
if exist "%SCRIPT_DIR%generate_mock_fixtures.py" (
    cd /d "%SCRIPT_DIR%"
    %PYTHON_CMD% generate_mock_fixtures.py
    if %errorlevel% equ 0 (
        call :print_success "Fixtures generated successfully"
    ) else (
        call :print_error "Failed to generate fixtures"
        exit /b 1
    )
) else (
    call :print_error "Fixture generator not found"
    exit /b 1
)
goto :eof

REM Function to start the server
:start_server
call :print_status "Starting Visual DM Mock Server..."
call :print_status "Host: %HOST%"
call :print_status "Port: %PORT%"
call :print_status "Debug: %DEBUG%"

call :check_port %PORT%
if %errorlevel% equ 0 (
    call :print_error "Port %PORT% is already in use"
    call :print_status "You can:"
    call :print_status "  1. Stop the process using port %PORT%"
    call :print_status "  2. Use a different port with --port <PORT>"
    exit /b 1
)

cd /d "%SCRIPT_DIR%"

set SERVER_CMD=%PYTHON_CMD% mock_server.py --host %HOST% --port %PORT%
if "%DEBUG%" == "true" (
    set SERVER_CMD=%SERVER_CMD% --debug
)

call :print_success "Server starting..."
call :print_status "URL: http://%HOST%:%PORT%"
call :print_status "Health check: http://%HOST%:%PORT%/health"
call :print_status "Press Ctrl+C to stop"
echo.

%SERVER_CMD%
goto :eof

REM Function to show usage
:show_usage
echo Visual DM Mock Server Startup Script
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --host HOST           Host to bind to (default: %DEFAULT_HOST%)
echo   --port PORT           Port to bind to (default: %DEFAULT_PORT%)
echo   --debug               Enable debug mode
echo   --install-deps        Install dependencies only
echo   --generate-fixtures   Generate fixtures only
echo   --help                Show this help message
echo.
echo Examples:
echo   %~nx0                                     # Start with defaults
echo   %~nx0 --host 0.0.0.0 --port 8080        # Bind to all interfaces on port 8080
echo   %~nx0 --debug                            # Start in debug mode
echo   %~nx0 --install-deps                     # Install dependencies only
goto :eof

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :main

if "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--debug" (
    set DEBUG=true
    shift
    goto :parse_args
)

if "%~1"=="--install-deps" (
    set INSTALL_DEPS_ONLY=true
    shift
    goto :parse_args
)

if "%~1"=="--generate-fixtures" (
    set GENERATE_FIXTURES_ONLY=true
    shift
    goto :parse_args
)

if "%~1"=="--help" (
    call :show_usage
    exit /b 0
)

call :print_error "Unknown option: %~1"
call :show_usage
exit /b 1

REM Main execution
:main
call :print_status "Visual DM Mock Server Setup"
echo =================================

REM Install dependencies if requested or needed
if "%INSTALL_DEPS_ONLY%" == "true" (
    call :install_dependencies
    if %errorlevel% neq 0 exit /b 1
    call :print_success "Dependencies installation complete"
    exit /b 0
)

REM Generate fixtures if requested
if "%GENERATE_FIXTURES_ONLY%" == "true" (
    call :generate_fixtures
    if %errorlevel% neq 0 exit /b 1
    call :print_success "Fixture generation complete"
    exit /b 0
)

REM Full setup and start
call :install_dependencies
if %errorlevel% neq 0 exit /b 1

call :generate_fixtures
if %errorlevel% neq 0 exit /b 1

call :start_server
exit /b %errorlevel% 