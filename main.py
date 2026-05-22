import pygame
import os
import random

# Configuration
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FIELD_SIZE = 500
FIELD_RECT = pygame.Rect((SCREEN_WIDTH - FIELD_SIZE) // 2, (SCREEN_HEIGHT - FIELD_SIZE) // 2, FIELD_SIZE, FIELD_SIZE)
ASSETS_DIR = r"C:\Users\藤本　羽奏\puzzle"

# Colors
COLOR_BG = (200, 230, 255)  # Light water blue
COLOR_FIELD = (255, 255, 255, 100)
COLOR_TEXT = (50, 50, 100)

class PuzzlePiece:
    def __init__(self, name, image_path, target_pos):
        self.name = name
        self.original_image = pygame.image.load(image_path).convert_alpha()
        
        # Scale image if too large
        max_size = 150
        w, h = self.original_image.get_size()
        if w > max_size or h > max_size:
            scale = max_size / max(w, h)
            self.original_image = pygame.transform.smoothscale(self.original_image, (int(w * scale), int(h * scale)))

        self.rotation = random.choice([0, 90, 180, 270])
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        # Target position is relative to the center of the field
        self.target_pos = target_pos
        self.target_rotation = 0 # Default target rotation is 0
        
        # Randomized start position
        self.rect.center = (random.randint(50, 200), random.randint(50, SCREEN_HEIGHT - 50))
        if random.random() > 0.5:
            self.rect.centerx = random.randint(SCREEN_WIDTH - 200, SCREEN_WIDTH - 50)

        self.dragging = False
        self.placed = False
        self.offset_x = 0
        self.offset_y = 0

    def rotate(self):
        if self.placed:
            return
        self.rotation = (self.rotation + 90) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, mouse_pos):
        if self.dragging:
            self.rect.centerx = mouse_pos[0] + self.offset_x
            self.rect.centery = mouse_pos[1] + self.offset_y

    def check_snap(self):
        if self.placed:
            return
        
        # Distance to target
        dist = pygame.Vector2(self.rect.center).distance_to(self.target_pos)
        
        if dist < 30 and self.rotation == self.target_rotation:
            self.rect.center = self.target_pos
            self.placed = True
            self.dragging = False
            return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.placed:
            # Add a subtle glow or indicator
            pygame.draw.rect(screen, (100, 255, 100), self.rect, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("水生生物パズルゲーム")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Meiryo", 36)

    # Load assets
    pieces = []
    animal_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.png')]
    
    # Define a simple grid layout for target positions
    # We have 12 animals. 4x3 grid inside the field.
    grid_cols = 4
    grid_rows = 3
    padding = FIELD_SIZE // max(grid_cols, grid_rows)
    
    for i, filename in enumerate(animal_files):
        name = os.path.splitext(filename)[0]
        col = i % grid_cols
        row = i // grid_cols
        
        # Calculate target position within the FIELD_RECT
        tx = FIELD_RECT.left + (col + 0.5) * (FIELD_SIZE / grid_cols)
        ty = FIELD_RECT.top + (row + 0.5) * (FIELD_SIZE / grid_rows)
        
        piece = PuzzlePiece(name, os.path.join(ASSETS_DIR, filename), (tx, ty))
        pieces.append(piece)

    running = True
    active_piece = None
    game_cleared = False

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Check pieces from top to bottom (reverse list)
                    for piece in reversed(pieces):
                        if not piece.placed and piece.rect.collidepoint(event.pos):
                            # Pixel perfect check
                            pos_in_mask = event.pos[0] - piece.rect.x, event.pos[1] - piece.rect.y
                            if piece.mask.get_at(pos_in_mask):
                                piece.dragging = True
                                piece.offset_x = piece.rect.centerx - event.pos[0]
                                piece.offset_y = piece.rect.centery - event.pos[1]
                                active_piece = piece
                                # Move to front
                                pieces.remove(piece)
                                pieces.append(piece)
                                break
                
                elif event.button == 3: # Right click to rotate
                    for piece in reversed(pieces):
                        if not piece.placed and piece.rect.collidepoint(event.pos):
                            pos_in_mask = event.pos[0] - piece.rect.x, event.pos[1] - piece.rect.y
                            if piece.mask.get_at(pos_in_mask):
                                piece.rotate()
                                piece.check_snap()
                                break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and active_piece:
                    active_piece.dragging = False
                    active_piece.check_snap()
                    active_piece = None
                    
                    # Check win condition
                    if all(p.placed for p in pieces):
                        game_cleared = True

        # Update
        if active_piece:
            active_piece.update(mouse_pos)

        # Draw
        screen.fill(COLOR_BG)
        
        # Draw Field
        pygame.draw.rect(screen, (220, 240, 255), FIELD_RECT)
        pygame.draw.rect(screen, (150, 180, 220), FIELD_RECT, 3)
        
        # Draw Grid Hints (Optional)
        for i in range(1, grid_cols):
            x = FIELD_RECT.left + i * (FIELD_SIZE / grid_cols)
            pygame.draw.line(screen, (200, 220, 240), (x, FIELD_RECT.top), (x, FIELD_RECT.bottom))
        for i in range(1, grid_rows):
            y = FIELD_RECT.top + i * (FIELD_SIZE / grid_rows)
            pygame.draw.line(screen, (200, 220, 240), (FIELD_RECT.left, y), (FIELD_RECT.right, y))

        # Draw Pieces
        for piece in pieces:
            piece.draw(screen)

        # UI
        title_surf = font.render("水生生物パズル", True, COLOR_TEXT)
        screen.blit(title_surf, (20, 20))
        
        hint_surf = font.render("左ドラッグ: 移動 / 右クリック: 回転", True, COLOR_TEXT)
        screen.blit(hint_surf, (20, SCREEN_HEIGHT - 50))

        if game_cleared:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            win_surf = font.render("全クリア！おめでとうございます！", True, (255, 255, 255))
            win_rect = win_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(win_surf, win_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
