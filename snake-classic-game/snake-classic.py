import tkinter as tk
import random
import time

# Game configuration
GAME_WIDTH = 600
GAME_HEIGHT = 400
SPEED = 100  # Milliseconds between moves
SPACE_SIZE = 20
SNAKE_HEAD_COLOR = "#00FF00"  # Bright green head
SNAKE_BODY_COLOR = "#32CD32"  # Lime green body
SNAKE_TAIL_COLOR = "#228B22"  # Forest green tail
FOOD_COLOR = "#FF0000"
BONUS_FOOD_COLOR = "#FFD700"  # Gold color for bonus food
BONUS_FOOD_SCORE = 10  # Score at which bonus food appears

# Enhanced scoring system
BASE_FOOD_POINTS = 10  # Base points for regular food
BONUS_FOOD_POINTS = 50  # Points for bonus food
STAGE_MULTIPLIERS = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0}  # Stage point multipliers
COMBO_THRESHOLD = 3  # Foods eaten quickly for combo bonus
COMBO_BONUS = 25  # Extra points for combo
SPEED_BONUS_THRESHOLD = 50  # Minimum delay for speed bonus
SPEED_BONUS_POINTS = 5  # Extra points for fast eating

# Stage system configuration
STAGE_PROGRESSION = 5  # Foods eaten needed to advance to next stage
STAGE_BACKGROUNDS = {
    1: "#000000",  # Stage 1: Black (Classic)
    2: "#001122",  # Stage 2: Dark Blue (Ocean)
    3: "#220011",  # Stage 3: Dark Purple (Cave)
    4: "#112200",  # Stage 4: Dark Green (Forest)
    5: "#221100"   # Stage 5: Dark Brown (Desert)
}
STAGE_NAMES = {
    1: "Classic Arena",
    2: "Ocean Depths", 
    3: "Crystal Caves",
    4: "Jungle Territory",
    5: "Desert Wasteland"
}
STAGE_EFFECTS = {
    1: {"stars": True, "count": 50},
    2: {"bubbles": True, "count": 30, "waves": True},
    3: {"crystals": True, "count": 25, "sparkles": True},
    4: {"leaves": True, "count": 40, "vines": True},
    5: {"sand": True, "count": 35, "dunes": True}
}

class Snake:
    def __init__(self):
        self.body_size = 3
        self.coordinates = [[0, 0]]
        self.squares = []
        for i in range(1, self.body_size):
            self.coordinates.append([0, i*SPACE_SIZE])

class Food:
    def __init__(self, canvas, snake):
        self.canvas = canvas
        self.place_new(snake)

    def place_new(self, snake):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if [x, y] not in snake.coordinates:
                break
        self.x = x
        self.y = y
        # Enhanced food design with gradient effect
        self.square = self.canvas.create_oval(
            x + 3, y + 3, x + SPACE_SIZE - 3, y + SPACE_SIZE - 3,
            fill=FOOD_COLOR, outline="#FF6666", width=2, tag="food"
        )
        
class BonusFood:
    def __init__(self, canvas, snake, regular_food):
        self.canvas = canvas
        self.place_new(snake, regular_food)

    def place_new(self, snake, regular_food):
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if ([x, y] not in snake.coordinates and 
                x != regular_food.x and y != regular_food.y):
                break
        self.x = x
        self.y = y
        # Enhanced bonus food with star-like appearance
        self.square = self.canvas.create_oval(
            x + 1, y + 1, x + SPACE_SIZE - 1, y + SPACE_SIZE - 1,
            fill=BONUS_FOOD_COLOR, outline="#FFA500", width=3, tag="bonus_food"
        )
        # Add sparkle effect
        sparkle = self.canvas.create_text(
            x + SPACE_SIZE//2, y + SPACE_SIZE//2,
            text="★", fill="#FFFFFF", font=("Arial", 8), tag="bonus_food"
        )
        
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game (Tkinter)")
        self.score = 0
        self.stage = 1
        self.current_bg_color = STAGE_BACKGROUNDS[1]
        self.bg_elements = []  # Store background animation elements
        self.animation_counter = 0
        
        # Enhanced scoring tracking
        self.combo_count = 0
        self.last_food_time = 0
        self.total_foods_eaten = 0
        self.stage_foods_eaten = 0

        self.label = tk.Label(root, text=f"Score: {self.score} | Stage: {self.stage} - {STAGE_NAMES[1]}", font=('consolas', 16))
        self.label.pack()

        self.canvas = tk.Canvas(root, bg=self.current_bg_color, height=GAME_HEIGHT, width=GAME_WIDTH)
        self.canvas.pack()

        self.reset()

        root.bind('<Left>', lambda event: self.change_direction('left'))
        root.bind('<Right>', lambda event: self.change_direction('right'))
        root.bind('<Up>', lambda event: self.change_direction('up'))
        root.bind('<Down>', lambda event: self.change_direction('down'))

        self.running = True
        self.next_move()

    def reset(self):
        self.direction = 'right'
        self.snake = Snake()
        self.draw_snake()
        
        self.food = Food(self.canvas, self.snake)
        self.bonus_food = None
        self.bonus_food_spawned = False  # Track if bonus food has been spawned
        
        self.score = 0
        self.stage = 1
        self.current_bg_color = STAGE_BACKGROUNDS[1]
        self.canvas.config(bg=self.current_bg_color)
        self.bg_elements = []
        self.animation_counter = 0
        
        # Reset scoring variables
        self.combo_count = 0
        self.last_food_time = 0
        self.total_foods_eaten = 0
        self.stage_foods_eaten = 0
        
        self.create_background_effects()
        self.update_display()

    def draw_snake(self):
        for square in self.snake.squares:
            self.canvas.delete(square)
        self.snake.squares = []
        
        for i, (x, y) in enumerate(self.snake.coordinates):
            # Determine color based on position in snake
            if i == 0:  # Head
                color = SNAKE_HEAD_COLOR
                # Draw head as circle with eyes
                square = self.canvas.create_oval(
                    x + 2, y + 2, x + SPACE_SIZE - 2, y + SPACE_SIZE - 2, 
                    fill=color, outline="#FFFFFF", width=2, tag="snake"
                )
                # Add eyes
                eye_size = 3
                eye1_x, eye1_y = x + 5, y + 5
                eye2_x, eye2_y = x + 12, y + 5
                eye1 = self.canvas.create_oval(
                    eye1_x, eye1_y, eye1_x + eye_size, eye1_y + eye_size,
                    fill="#000000", tag="snake"
                )
                eye2 = self.canvas.create_oval(
                    eye2_x, eye2_y, eye2_x + eye_size, eye2_y + eye_size,
                    fill="#000000", tag="snake"
                )
                self.snake.squares.extend([square, eye1, eye2])
            elif i == len(self.snake.coordinates) - 1:  # Tail
                color = SNAKE_TAIL_COLOR
                square = self.canvas.create_oval(
                    x + 3, y + 3, x + SPACE_SIZE - 3, y + SPACE_SIZE - 3, 
                    fill=color, outline=SNAKE_BODY_COLOR, width=1, tag="snake"
                )
                self.snake.squares.append(square)
            else:  # Body
                color = SNAKE_BODY_COLOR
                square = self.canvas.create_rectangle(
                    x + 1, y + 1, x + SPACE_SIZE - 1, y + SPACE_SIZE - 1, 
                    fill=color, outline=SNAKE_HEAD_COLOR, width=1, tag="snake"
                )
                self.snake.squares.append(square)

    def next_move(self):
        if not self.running:
            return

        x, y = self.snake.coordinates[0]

        if self.direction == 'up':
            y -= SPACE_SIZE
        elif self.direction == 'down':
            y += SPACE_SIZE
        elif self.direction == 'left':
            x -= SPACE_SIZE
        elif self.direction == 'right':
            x += SPACE_SIZE

        # Handle edge wrapping
        x = self.wrap_coordinate(x, GAME_WIDTH)
        y = self.wrap_coordinate(y, GAME_HEIGHT)

        new_head = [x, y]

        # Check only for self-collision
        if self.check_self_collision(new_head):
            self.game_over()
            return

        self.snake.coordinates.insert(0, new_head)

        # Check collision with regular food
        if x == self.food.x and y == self.food.y:
            points_earned = self.calculate_food_points()
            self.score += points_earned
            self.total_foods_eaten += 1
            self.stage_foods_eaten += 1
            self.show_points_popup(x, y, points_earned)
            self.canvas.delete(self.food.square)
            self.food = Food(self.canvas, self.snake)
            
            # Check for stage progression (based on foods eaten, not score)
            new_stage = min(5, (self.total_foods_eaten // STAGE_PROGRESSION) + 1)
            if new_stage != self.stage:
                self.stage = new_stage
                self.current_bg_color = STAGE_BACKGROUNDS.get(self.stage, STAGE_BACKGROUNDS[5])
                self.canvas.config(bg=self.current_bg_color)
                self.clear_background_effects()
                self.create_background_effects()
                self.show_stage_message()
            
            # Spawn bonus food only once at specific food count
            if self.total_foods_eaten == BONUS_FOOD_SCORE and not self.bonus_food_spawned:
                self.bonus_food = BonusFood(self.canvas, self.snake, self.food)
                self.bonus_food_spawned = True
            
            self.update_display()
                
        # Check collision with bonus food (if it exists)
        elif self.bonus_food and x == self.bonus_food.x and y == self.bonus_food.y:
            bonus_points = self.calculate_bonus_food_points()
            self.score += bonus_points
            self.total_foods_eaten += 1
            self.stage_foods_eaten += 1
            self.show_points_popup(x, y, bonus_points, is_bonus=True)
            self.canvas.delete(self.bonus_food.square)
            self.bonus_food = None
            self.update_display()
        else:
            # No food eaten, remove tail
            self.snake.coordinates.pop()

        self.draw_snake()
        
        # Animate background effects
        self.animate_background()
        
        # Adjust speed based on score
        current_speed = self.get_current_speed()
        self.root.after(current_speed, self.next_move)

    def change_direction(self, new_direction):
        opposites = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
        if opposites[new_direction] != self.direction:
            self.direction = new_direction

    def wrap_coordinate(self, coord, max_size):
        """Wrap coordinate around the game boundary"""
        if coord < 0:
            return max_size - SPACE_SIZE
        elif coord >= max_size:
            return 0
        return coord
    
    def check_self_collision(self, head):
        """Check if the snake collides with itself"""
        return head in self.snake.coordinates
    
    def update_display(self):
        """Update score and stage display"""
        stage_name = STAGE_NAMES.get(self.stage, "Unknown")
        multiplier = STAGE_MULTIPLIERS.get(self.stage, 1.0)
        
        # Calculate progress to next stage
        foods_in_current_stage = self.total_foods_eaten % STAGE_PROGRESSION
        foods_needed = STAGE_PROGRESSION - foods_in_current_stage
        
        combo_text = f" | COMBO x{self.combo_count}" if self.combo_count >= COMBO_THRESHOLD else ""
        progress_text = f" | Next: {foods_needed} foods" if self.stage < 5 else " | MAX STAGE"
        
        self.label.config(text=f"Score: {self.score} | Stage: {self.stage} - {stage_name} (x{multiplier}){combo_text}{progress_text}")
    
    def calculate_food_points(self):
        """Calculate points for regular food with bonuses"""
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Base points
        points = BASE_FOOD_POINTS
        
        # Stage multiplier
        multiplier = STAGE_MULTIPLIERS.get(self.stage, 1.0)
        points = int(points * multiplier)
        
        # Combo bonus (eating foods quickly)
        time_diff = current_time - self.last_food_time if self.last_food_time > 0 else float('inf')
        if time_diff < 2000:  # Within 2 seconds
            self.combo_count += 1
            if self.combo_count >= COMBO_THRESHOLD:
                points += COMBO_BONUS
        else:
            self.combo_count = 1
        
        # Speed bonus (if game is fast)
        current_speed = self.get_current_speed()
        if current_speed <= SPEED_BONUS_THRESHOLD:
            points += SPEED_BONUS_POINTS
        
        self.last_food_time = current_time
        return points
    
    def calculate_bonus_food_points(self):
        """Calculate points for bonus food"""
        points = BONUS_FOOD_POINTS
        multiplier = STAGE_MULTIPLIERS.get(self.stage, 1.0)
        return int(points * multiplier)
    
    def show_points_popup(self, x, y, points, is_bonus=False):
        """Show floating points popup"""
        color = "#FFD700" if is_bonus else "#00FF00"
        text = f"+{points}"
        if self.combo_count >= COMBO_THRESHOLD:
            text += f" COMBO!"
        
        popup = self.canvas.create_text(
            x + SPACE_SIZE//2, y - 10,
            text=text, fill=color, font=("Arial", 12, "bold")
        )
        
        # Animate popup moving up and fading
        def animate_popup(step=0):
            if step < 20:
                self.canvas.move(popup, 0, -2)
                self.root.after(50, lambda: animate_popup(step + 1))
            else:
                self.canvas.delete(popup)
        
        animate_popup()
    
    def show_stage_message(self):
        """Show stage advancement message"""
        stage_name = STAGE_NAMES.get(self.stage, "Unknown")
        message = self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2,
            font=('consolas', 24),
            fill="#FFFFFF",
            text=f"STAGE {self.stage}\n{stage_name}"
        )
        # Remove message after 2 seconds
        self.root.after(2000, lambda: self.canvas.delete(message))
    
    def clear_background_effects(self):
        """Clear all background elements"""
        for element in self.bg_elements:
            self.canvas.delete(element)
        self.bg_elements = []
    
    def create_background_effects(self):
        """Create stage-specific background effects"""
        effects = STAGE_EFFECTS.get(self.stage, {})
        
        if self.stage == 1:  # Stars
            for _ in range(effects.get("count", 50)):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                star = self.canvas.create_text(x, y, text="✦", fill="#FFFFFF", font=("Arial", random.randint(6, 12)), tags="background")
                self.bg_elements.append(star)
                
        elif self.stage == 2:  # Ocean bubbles and waves
            # Bubbles
            for _ in range(effects.get("count", 30)):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                size = random.randint(3, 8)
                bubble = self.canvas.create_oval(x, y, x + size, y + size, outline="#4488CC", width=1, tags="background")
                self.bg_elements.append(bubble)
            # Wave lines
            for i in range(5):
                y = i * 80 + 50
                wave = self.canvas.create_line(0, y, GAME_WIDTH, y + 20, fill="#003366", width=2, smooth=True, tags="background")
                self.bg_elements.append(wave)
                
        elif self.stage == 3:  # Crystal caves
            # Crystals
            for _ in range(effects.get("count", 25)):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                crystal = self.canvas.create_text(x, y, text="◆", fill="#AA44AA", font=("Arial", random.randint(8, 16)), tags="background")
                self.bg_elements.append(crystal)
            # Sparkles
            for _ in range(20):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                sparkle = self.canvas.create_text(x, y, text="✨", fill="#FFAAFF", font=("Arial", 6), tags="background")
                self.bg_elements.append(sparkle)
                
        elif self.stage == 4:  # Jungle
            # Leaves
            for _ in range(effects.get("count", 40)):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                leaf = self.canvas.create_text(x, y, text="🍃", fill="#44AA44", font=("Arial", random.randint(8, 14)), tags="background")
                self.bg_elements.append(leaf)
            # Vine patterns
            for i in range(3):
                x = i * 200 + 100
                vine = self.canvas.create_line(x, 0, x + 50, GAME_HEIGHT, fill="#226622", width=3, tags="background")
                self.bg_elements.append(vine)
                
        elif self.stage == 5:  # Desert
            # Sand dunes
            for i in range(4):
                x = i * 150
                dune = self.canvas.create_arc(x, GAME_HEIGHT - 60, x + 200, GAME_HEIGHT, start=0, extent=180, outline="#AA8844", width=2, tags="background")
                self.bg_elements.append(dune)
            # Sand particles
            for _ in range(effects.get("count", 35)):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                sand = self.canvas.create_oval(x, y, x + 2, y + 2, fill="#CCAA66", outline="#CCAA66", tags="background")
                self.bg_elements.append(sand)
    
    def animate_background(self):
        """Animate background elements"""
        self.animation_counter += 1
        
        if self.stage == 1:  # Twinkling stars
            if self.animation_counter % 30 == 0:  # Every 30 frames
                for element in self.bg_elements[:10]:  # Animate some stars
                    if random.random() < 0.3:
                        current_color = self.canvas.itemcget(element, "fill")
                        new_color = "#FFFF00" if current_color == "#FFFFFF" else "#FFFFFF"
                        self.canvas.itemconfig(element, fill=new_color)
                        
        elif self.stage == 2:  # Moving bubbles
            if self.animation_counter % 20 == 0:
                for i, element in enumerate(self.bg_elements[:30]):
                    if i < 30:  # Only bubbles
                        coords = self.canvas.coords(element)
                        if len(coords) == 4:
                            self.canvas.move(element, 0, -2)
                            # Reset bubble if it goes off screen
                            if coords[1] < 0:
                                self.canvas.coords(element, coords[0], GAME_HEIGHT, coords[2], GAME_HEIGHT + (coords[3] - coords[1]))
    
    def get_current_speed(self):
        """Calculate current game speed based on score"""
        if self.score > 15:
            # Speed up the game - lower delay means faster movement
            return max(50, SPEED - (self.score - 15) * 5)  # Minimum 50ms delay
        return SPEED

    def game_over(self):
        self.running = False
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2,
            font=('consolas', 40),
            fill="red",
            text="GAME OVER!"
        )

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
