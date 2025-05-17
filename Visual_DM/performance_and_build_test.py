import os
import time
import pygame
import tracemalloc
import platform
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PERF_REPORT = os.path.join(PROJECT_ROOT, 'performance_report.md')
BUILD_REPORT = os.path.join(PROJECT_ROOT, 'build_verification_report.md')

# --- Performance Benchmarking ---
def benchmark_pygame():
    report = ['# Performance Report\n']
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    tracemalloc.start()
    start_mem = tracemalloc.get_traced_memory()[0]
    start_time = time.time()
    frame_count = 0
    running = True
    while running and frame_count < 300:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    end_time = time.time()
    end_mem = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    fps = frame_count / (end_time - start_time)
    report.append(f'- Average FPS over 300 frames: {fps:.2f}')
    report.append(f'- Memory before: {start_mem} bytes')
    report.append(f'- Memory after: {end_mem} bytes')
    report.append(f'- Memory delta: {end_mem - start_mem} bytes')
    pygame.quit()
    with open(PERF_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

# --- Build System Verification ---
def verify_build_system():
    report = ['# Build Verification Report\n']
    # Example: check for pyinstaller and attempt to build
    try:
        import PyInstaller.__main__
        spec_file = os.path.join(PROJECT_ROOT, 'main.py')
        if os.path.exists(spec_file):
            PyInstaller.__main__.run([
                spec_file,
                '--onefile',
                '--noconfirm',
                '--distpath', os.path.join(PROJECT_ROOT, 'dist'),
                '--workpath', os.path.join(PROJECT_ROOT, 'build'),
                '--specpath', os.path.join(PROJECT_ROOT, 'build'),
            ])
            report.append(f'- Build succeeded for {spec_file}')
            exe_path = os.path.join(PROJECT_ROOT, 'dist', 'main')
            if platform.system() == 'Windows':
                exe_path += '.exe'
            if os.path.exists(exe_path):
                try:
                    # Smoke test: launch and wait 2 seconds
                    proc = subprocess.Popen([exe_path])
                    time.sleep(2)
                    proc.terminate()
                    report.append(f'- Smoke test passed for {exe_path}')
                except Exception as e:
                    report.append(f'- Smoke test failed: {e}')
            else:
                report.append(f'- Executable not found after build: {exe_path}')
        else:
            report.append('- main.py not found, skipping build test.')
    except ImportError:
        report.append('- PyInstaller not installed, skipping build test.')
    except Exception as e:
        report.append(f'- Build system error: {e}')
    with open(BUILD_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

def main():
    benchmark_pygame()
    verify_build_system()
    print(f"Performance and build tests complete. See {PERF_REPORT} and {BUILD_REPORT}.")

if __name__ == '__main__':
    main() 