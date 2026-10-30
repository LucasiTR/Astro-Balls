import pygame

def create_fading_text(text, font, top_color, bottom_color, overall_alpha=180):
    """
    Renders text with a top-to-bottom color gradient and custom opacity.
    Returns a static pygame.Surface optimized for blitting.
    """
    # Render the raw text layer in solid white
    text_mask = font.render(text, True, (255, 255, 255))
    width, height = text_mask.get_size()

    # Create the destination surface with alpha channel support
    text_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Build a vertical gradient overlay
    gradient_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        ratio = y / float(height) if height > 1 else 0.0

        # Calculate color transitions per row
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)

        pygame.draw.line(gradient_surf, (r, g, b, 255), (0, y), (width, y))

    # Construct the final composited surface
    text_surface.blit(text_mask, (0, 0))
    text_surface.blit(gradient_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Apply overall alpha translucency
    text_surface.set_alpha(overall_alpha)

    return text_surface
