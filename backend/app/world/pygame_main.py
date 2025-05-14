import pygame
import sys
import json
import os
import psutil
import time

# Load window config from config.json if available, else use defaults
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../../config.json')
def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config.get('window', {})
    except Exception:
        return {}

config = load_config()
WINDOW_WIDTH = config.get('width', 1024)
WINDOW_HEIGHT = config.get('height', 768)
WINDOW_TITLE = config.get('title', 'Region Map Display System')

# Initialize pygame
pygame.init()

# Create a resizable window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(WINDOW_TITLE)

# Track current window size for use by rendering and logic code
current_width = WINDOW_WIDTH
current_height = WINDOW_HEIGHT

# Optionally, create a ViewportManager instance (future integration)
try:
    from viewport_manager import ViewportManager
    viewport = ViewportManager(width=current_width, height=current_height)
except ImportError:
    viewport = None

# Set target FPS
TARGET_FPS = 60
clock = pygame.time.Clock()

# Timing variables
elapsed_time = 0.0

# Performance metrics tracking
FPS_SAMPLES = 60
fps_history = []
frame_time_history = []
process = psutil.Process(os.getpid())

# Debug overlay toggle
show_debug_overlay = True

def get_memory_usage_mb():
    mem_bytes = process.memory_info().rss
    return mem_bytes / (1024 * 1024)

def get_smoothed_fps():
    if not fps_history:
        return 0.0
    return sum(fps_history) / len(fps_history)

def get_smoothed_frame_time():
    if not frame_time_history:
        return 0.0
    return sum(frame_time_history) / len(frame_time_history)

# Overlay rendering function
def render_debug_overlay(screen, info_font, current_fps, elapsed_time, smoothed_fps, smoothed_frame_time, mem_mb, current_width, current_height):
    lines = [
        f'FPS: {current_fps:.1f}',
        f'Elapsed: {elapsed_time:.2f}s',
        f'Avg FPS: {smoothed_fps:.1f} | Frame: {smoothed_frame_time:.2f} ms',
        f'Mem: {mem_mb:.1f} MB',
        f'Window: {current_width}x{current_height}'
    ]
    y = 10
    for line in lines:
        text = info_font.render(line, True, (220, 220, 220))
        screen.blit(text, (10, y))
        y += 26

# Main event loop
running = True
while running:
    frame_start = time.perf_counter()
    dt = clock.tick(TARGET_FPS) / 1000.0  # Delta time in seconds
    elapsed_time += dt
    current_fps = clock.get_fps()
    # Track FPS and frame time for rolling average
    fps_history.append(current_fps)
    if len(fps_history) > FPS_SAMPLES:
        fps_history.pop(0)
    frame_time_ms = (time.perf_counter() - frame_start) * 1000.0
    frame_time_history.append(frame_time_ms)
    if len(frame_time_history) > FPS_SAMPLES:
        frame_time_history.pop(0)
    # Optionally, show FPS in window title for debug
    pygame.display.set_caption(f"{WINDOW_TITLE} - FPS: {current_fps:.1f}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # Update the display surface to the new size
            current_width, current_height = event.w, event.h
            screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
            # Update viewport size if using ViewportManager
            if viewport is not None:
                viewport.set_state(width=current_width, height=current_height)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                show_debug_overlay = not show_debug_overlay
    # Fill the screen with a background color
    screen.fill((30, 30, 40))
    # Draw a simple message (optional)
    font = pygame.font.SysFont(None, 36)
    text = font.render('Region Map Display System', True, (200, 200, 220))
    screen.blit(text, (40, 40))
    # Draw debug overlay if enabled
    info_font = pygame.font.SysFont(None, 24)
    smoothed_fps = get_smoothed_fps()
    smoothed_frame_time = get_smoothed_frame_time()
    mem_mb = get_memory_usage_mb()
    if show_debug_overlay:
        render_debug_overlay(screen, info_font, current_fps, elapsed_time, smoothed_fps, smoothed_frame_time, mem_mb, current_width, current_height)
    # Update the display
    pygame.display.flip()

# Clean up and exit
pygame.quit()
sys.exit() 