"""Region rendering module."""

from typing import List, Tuple, Dict
import numpy as np
from PIL import Image, ImageDraw
from .region import Region
from .viewport import ViewportManager

class RegionRenderer:
    """Handles rendering of regions."""
    
    def __init__(self, viewport: ViewportManager):
        """Initialize renderer.
        
        Args:
            viewport: Viewport manager instance
        """
        self.viewport = viewport
        self.background_color = (255, 255, 255)  # White background
        
    def _create_image(self) -> Image.Image:
        """Create a new image for rendering.
        
        Returns:
            PIL Image object
        """
        return Image.new(
            'RGBA',
            (int(self.viewport.width), int(self.viewport.height)),
            self.background_color
        )
        
    def _transform_points(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Transform world space points to screen space.
        
        Args:
            points: List of (x, y) coordinates in world space
            
        Returns:
            List of (x, y) coordinates in screen space
        """
        return [self.viewport.world_to_screen(p) for p in points]
        
    def _draw_region(
        self,
        draw: ImageDraw.ImageDraw,
        region: Region,
        alpha: int = 255
    ) -> None:
        """Draw a single region.
        
        Args:
            draw: PIL ImageDraw object
            region: Region to draw
            alpha: Alpha value for fill color (0-255)
        """
        # Get region data
        render_data = region.get_render_data()
        
        # Transform boundary points to screen space
        screen_points = self._transform_points(render_data["boundary"])
        
        # Add alpha channel to colors
        fill_color = (*render_data["color"], alpha)
        border_color = (*render_data["border_color"], 255)  # Border always fully opaque
        
        # Draw region
        if render_data["is_visible"]:
            # Draw fill
            draw.polygon(screen_points, fill=fill_color)
            
            # Draw border
            draw.line(
                screen_points + [screen_points[0]],  # Close the polygon
                fill=border_color,
                width=max(1, int(2 * self.viewport.zoom))  # Scale border with zoom
            )
            
            # Draw selection/hover indicators
            if render_data["is_selected"] or render_data["is_hovered"]:
                indicator_color = (255, 255, 0, 255) if render_data["is_selected"] else (255, 255, 255, 255)
                draw.line(
                    screen_points + [screen_points[0]],
                    fill=indicator_color,
                    width=max(2, int(3 * self.viewport.zoom))
                )
                
    def render_regions(
        self,
        regions: List[Region],
        format: str = 'PNG'
    ) -> bytes:
        """Render multiple regions to an image.
        
        Args:
            regions: List of regions to render
            format: Output image format ('PNG' or 'JPEG')
            
        Returns:
            Rendered image as bytes
        """
        # Create image and drawing context
        image = self._create_image()
        draw = ImageDraw.Draw(image)
        
        # Sort regions by z-index
        sorted_regions = sorted(regions, key=lambda r: r.properties.z_index)
        
        # Draw regions
        for region in sorted_regions:
            self._draw_region(draw, region)
            
        # Convert to bytes
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
        
    def render_region_labels(
        self,
        regions: List[Region],
        font_size: int = 12,
        format: str = 'PNG'
    ) -> bytes:
        """Render region labels as a separate layer.
        
        Args:
            regions: List of regions to render labels for
            font_size: Base font size in pixels
            format: Output image format ('PNG' or 'JPEG')
            
        Returns:
            Rendered label layer as bytes
        """
        # Create transparent image for labels
        image = Image.new(
            'RGBA',
            (int(self.viewport.width), int(self.viewport.height)),
            (0, 0, 0, 0)  # Transparent background
        )
        draw = ImageDraw.Draw(image)
        
        # Sort regions by z-index
        sorted_regions = sorted(regions, key=lambda r: r.properties.z_index)
        
        # Draw labels
        for region in sorted_regions:
            if region.properties.is_visible:
                # Get region center in world space
                center = np.array(region.boundary.centroid.coords[0])
                
                # Transform to screen space
                screen_center = self.viewport.world_to_screen(center)
                
                # Scale font size with zoom
                scaled_font_size = max(8, int(font_size * self.viewport.zoom))
                
                # Draw label
                label = region.properties.name
                bbox = draw.textbbox(screen_center, label, font_size=scaled_font_size)
                
                # Draw text background
                padding = 2
                draw.rectangle(
                    (
                        bbox[0] - padding,
                        bbox[1] - padding,
                        bbox[2] + padding,
                        bbox[3] + padding
                    ),
                    fill=(255, 255, 255, 200)
                )
                
                # Draw text
                draw.text(
                    screen_center,
                    label,
                    fill=(0, 0, 0, 255),
                    font_size=scaled_font_size,
                    anchor="mm"  # Center align
                )
                
        # Convert to bytes
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue() 