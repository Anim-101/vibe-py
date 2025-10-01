import tkinter as tk
import random
import time
import re

# Game configuration
GAME_WIDTH = 800
GAME_HEIGHT = 600
SPEED = 100  # Milliseconds between moves
SPACE_SIZE = 20
# Realistic snake colors with gradients
SNAKE_HEAD_COLORS = ["#00FF00", "#32FF32", "#00CC00"]  # Gradient green head
SNAKE_BODY_COLORS = ["#32CD32", "#50E050", "#28A428"]  # Gradient body segments
SNAKE_TAIL_COLOR = "#228B22"  # Forest green tail
SNAKE_OUTLINE = "#004400"  # Dark green outline

# Enhanced food colors
FOOD_GRADIENT = ["#FF0000", "#FF3333", "#CC0000"]  # Red gradient
FOOD_HIGHLIGHT = "#FFAAAA"  # Light highlight
BONUS_FOOD_GRADIENT = ["#FFD700", "#FFED4A", "#DAA520"]  # Gold gradient
BONUS_HIGHLIGHT = "#FFFFCC"  # Light gold highlight
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
VICTORY_FOODS = 25  # Foods needed to win the game (reach stage 6)
MAX_STAGE = 5  # Maximum stage number
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
        self.elements = []  # Store all visual elements
        self.place_new(snake)

    def place_new(self, snake):
        # Clear existing elements
        for element in self.elements:
            self.canvas.delete(element)
        self.elements = []
        
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if [x, y] not in snake.coordinates:
                break
        self.x = x
        self.y = y
        
        # Realistic apple design
        # Apple shadow
        shadow = self.canvas.create_oval(
            x + 5, y + 5, x + SPACE_SIZE - 1, y + SPACE_SIZE - 1,
            fill="#990000", tag="food"
        )
        # Main apple body
        apple_body = self.canvas.create_oval(
            x + 2, y + 3, x + SPACE_SIZE - 2, y + SPACE_SIZE - 2,
            fill=FOOD_GRADIENT[0], outline=FOOD_GRADIENT[2], width=2, tag="food"
        )
        # Apple highlight (3D effect)
        highlight = self.canvas.create_arc(
            x + 4, y + 5, x + 12, y + 13,
            start=45, extent=90, outline=FOOD_HIGHLIGHT, width=2, tag="food"
        )
        # Apple stem
        stem = self.canvas.create_rectangle(
            x + SPACE_SIZE//2 - 1, y + 1, x + SPACE_SIZE//2 + 1, y + 4,
            fill="#8B4513", tag="food"
        )
        # Apple leaf
        leaf = self.canvas.create_oval(
            x + SPACE_SIZE//2 + 1, y + 2, x + SPACE_SIZE//2 + 4, y + 4,
            fill="#228B22", tag="food"
        )
        
        self.elements = [shadow, apple_body, highlight, stem, leaf]
        self.square = apple_body  # Keep for compatibility
    
    def delete(self):
        """Delete all visual elements of the food"""
        for element in self.elements:
            self.canvas.delete(element)
        self.elements = []
        
class BonusFood:
    def __init__(self, canvas, snake, regular_food):
        self.canvas = canvas
        self.elements = []
        self.animation_phase = 0
        self.place_new(snake, regular_food)

    def place_new(self, snake, regular_food):
        # Clear existing elements
        for element in self.elements:
            self.canvas.delete(element)
        self.elements = []
        
        while True:
            x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            if ([x, y] not in snake.coordinates and 
                x != regular_food.x and y != regular_food.y):
                break
        self.x = x
        self.y = y
        
        # Realistic golden fruit with glow effect
        # Outer glow
        glow = self.canvas.create_oval(
            x - 2, y - 2, x + SPACE_SIZE + 2, y + SPACE_SIZE + 2,
            fill="", outline=BONUS_HIGHLIGHT, width=3, tag="bonus_food"
        )
        # Main golden fruit
        fruit_shadow = self.canvas.create_oval(
            x + 3, y + 3, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=BONUS_FOOD_GRADIENT[2], tag="bonus_food"
        )
        fruit_main = self.canvas.create_oval(
            x + 1, y + 1, x + SPACE_SIZE - 1, y + SPACE_SIZE - 1,
            fill=BONUS_FOOD_GRADIENT[0], outline=BONUS_FOOD_GRADIENT[2], width=2, tag="bonus_food"
        )
        # Golden highlight
        gold_highlight = self.canvas.create_arc(
            x + 3, y + 3, x + 12, y + 12,
            start=45, extent=90, outline="#FFFFAA", width=3, tag="bonus_food"
        )
        # Animated sparkles
        sparkle1 = self.canvas.create_text(
            x + 5, y + 5, text="✦", fill="#FFFFFF", font=("Arial", 6), tag="bonus_food"
        )
        sparkle2 = self.canvas.create_text(
            x + 15, y + 8, text="✧", fill="#FFFFCC", font=("Arial", 5), tag="bonus_food"
        )
        sparkle3 = self.canvas.create_text(
            x + 8, y + 15, text="✦", fill="#FFFF88", font=("Arial", 4), tag="bonus_food"
        )
        
        self.elements = [glow, fruit_shadow, fruit_main, gold_highlight, sparkle1, sparkle2, sparkle3]
        self.square = fruit_main  # Keep for compatibility
    
    def delete(self):
        """Delete all visual elements of the bonus food"""
        for element in self.elements:
            self.canvas.delete(element)
        self.elements = []
    
    def animate(self, canvas):
        """Animate the bonus food sparkles"""
        self.animation_phase = (self.animation_phase + 1) % 60
        if len(self.elements) >= 7:  # Ensure sparkles exist
            # Animate sparkles with pulsing effect
            alpha = 0.5 + 0.5 * abs(self.animation_phase - 30) / 30
            sparkle_colors = ["#FFFFFF", "#FFFFCC", "#FFFF88"]
            for i, sparkle in enumerate(self.elements[-3:]):
                if self.animation_phase % 20 == i * 7:
                    color = sparkle_colors[i % 3]
                    canvas.itemconfig(sparkle, fill=color)
        
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game - Vibe Python Edition")
        
        # Configure window size and appearance
        self.root.configure(bg='#000000')
        self.root.resizable(False, False)  # Fixed size window
        
        # Calculate window size including margins
        window_width = GAME_WIDTH + 20  # Add padding
        window_height = GAME_HEIGHT + 80  # Add space for label and padding
        
        # Center the window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
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
        self.game_won = False  # Track if player has won
        
        # Timestamp tracking
        self.start_time = time.time()
        self.session_start = time.strftime("%H:%M:%S", time.localtime(self.start_time))

        self.label = tk.Label(
            root, 
            text=f"Score: {self.score} | Stage: {self.stage} - {STAGE_NAMES[1]} | Time: 00:00", 
            font=('Courier', 14, 'bold'), 
            bg='#000000',
            fg='#00FF00',
            width=100,
            pady=5
        )
        self.label.pack(padx=10, pady=(5, 0))

        self.canvas = tk.Canvas(
            root, 
            bg=self.current_bg_color, 
            height=GAME_HEIGHT, 
            width=GAME_WIDTH,
            highlightthickness=2,
            highlightbackground='#333333',
            relief='solid',
            bd=1
        )
        self.canvas.pack(padx=10, pady=5, expand=False, fill=None)

        self.reset()

        root.bind('<Left>', lambda event: self.change_direction('left'))
        root.bind('<Right>', lambda event: self.change_direction('right'))
        root.bind('<Up>', lambda event: self.change_direction('up'))
        root.bind('<Down>', lambda event: self.change_direction('down'))

        self.running = True
        
        # Start real-time timestamp updates
        self.update_timestamp_display()
        
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
        self.game_won = False
        
        # Reset timestamp
        self.start_time = time.time()
        self.session_start = time.strftime("%H:%M:%S", time.localtime(self.start_time))
        
        # Restart real-time timestamp updates if game is running
        if hasattr(self, 'running') and self.running:
            self.root.after(100, self.update_timestamp_display)
        
        self.create_background_effects()
        self.update_display()

    def draw_snake(self):
        for square in self.snake.squares:
            self.canvas.delete(square)
        self.snake.squares = []
        
        snake_length = len(self.snake.coordinates)
        for i, (x, y) in enumerate(self.snake.coordinates):
            if i == 0:  # Head - realistic with 3D effect
                # Main head with gradient effect
                head_bg = self.canvas.create_oval(
                    x + 1, y + 1, x + SPACE_SIZE - 1, y + SPACE_SIZE - 1,
                    fill=SNAKE_HEAD_COLORS[2], outline=SNAKE_OUTLINE, width=2, tag="snake"
                )
                head_main = self.canvas.create_oval(
                    x + 2, y + 2, x + SPACE_SIZE - 2, y + SPACE_SIZE - 2,
                    fill=SNAKE_HEAD_COLORS[0], outline=SNAKE_HEAD_COLORS[1], width=1, tag="snake"
                )
                # 3D highlight
                highlight = self.canvas.create_arc(
                    x + 3, y + 3, x + SPACE_SIZE - 8, y + SPACE_SIZE - 8,
                    start=45, extent=90, outline="#FFFFFF", width=2, tag="snake"
                )
                
                # Realistic eyes with pupils
                eye_size = 4
                pupil_size = 2
                eye1_x, eye1_y = x + 6, y + 6
                eye2_x, eye2_y = x + 12, y + 6
                
                # Eye whites
                eye1_white = self.canvas.create_oval(
                    eye1_x, eye1_y, eye1_x + eye_size, eye1_y + eye_size,
                    fill="#FFFFFF", outline="#CCCCCC", tag="snake"
                )
                eye2_white = self.canvas.create_oval(
                    eye2_x, eye2_y, eye2_x + eye_size, eye2_y + eye_size,
                    fill="#FFFFFF", outline="#CCCCCC", tag="snake"
                )
                # Pupils
                eye1_pupil = self.canvas.create_oval(
                    eye1_x + 1, eye1_y + 1, eye1_x + pupil_size + 1, eye1_y + pupil_size + 1,
                    fill="#000000", tag="snake"
                )
                eye2_pupil = self.canvas.create_oval(
                    eye2_x + 1, eye2_y + 1, eye2_x + pupil_size + 1, eye2_y + pupil_size + 1,
                    fill="#000000", tag="snake"
                )
                
                self.snake.squares.extend([head_bg, head_main, highlight, eye1_white, eye2_white, eye1_pupil, eye2_pupil])
                
            elif i == snake_length - 1:  # Tail - tapered and realistic
                # Tapered tail effect
                tail_main = self.canvas.create_oval(
                    x + 4, y + 4, x + SPACE_SIZE - 4, y + SPACE_SIZE - 4,
                    fill=SNAKE_TAIL_COLOR, outline=SNAKE_OUTLINE, width=1, tag="snake"
                )
                tail_tip = self.canvas.create_oval(
                    x + 7, y + 7, x + SPACE_SIZE - 7, y + SPACE_SIZE - 7,
                    fill=SNAKE_BODY_COLORS[2], tag="snake"
                )
                self.snake.squares.extend([tail_main, tail_tip])
                
            else:  # Body - 3D segments with texture
                # Body segment gradient
                segment_index = i % 3
                body_color = SNAKE_BODY_COLORS[segment_index]
                
                # Main body segment
                body_bg = self.canvas.create_rectangle(
                    x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                    fill=SNAKE_BODY_COLORS[2], outline=SNAKE_OUTLINE, width=1, tag="snake"
                )
                body_main = self.canvas.create_rectangle(
                    x + 1, y + 1, x + SPACE_SIZE - 1, y + SPACE_SIZE - 1,
                    fill=body_color, tag="snake"
                )
                # 3D highlight strip
                highlight_strip = self.canvas.create_rectangle(
                    x + 2, y + 2, x + SPACE_SIZE - 2, y + 5,
                    fill=SNAKE_BODY_COLORS[1], tag="snake"
                )
                # Scale pattern
                if i % 2 == 0:
                    scale = self.canvas.create_line(
                        x + 4, y + SPACE_SIZE//2, x + SPACE_SIZE - 4, y + SPACE_SIZE//2,
                        fill=SNAKE_OUTLINE, width=1, tag="snake"
                    )
                    self.snake.squares.append(scale)
                    
                self.snake.squares.extend([body_bg, body_main, highlight_strip])

    def next_move(self):
        if not self.running or self.game_won:
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

        # Check only for self-collision (must have body segments to collide)
        if len(self.snake.coordinates) > 1 and self.check_self_collision(new_head):
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
            self.food.delete()  # Delete all food elements
            self.food = Food(self.canvas, self.snake)
            
            # Check for victory condition
            if self.total_foods_eaten >= VICTORY_FOODS and not self.game_won and self.running:
                self.game_won = True
                self.running = False  # Stop the game loop immediately
                self.show_victory_screen()
                return
            
            # Check for stage progression (based on foods eaten, not score)
            try:
                new_stage = min(MAX_STAGE, (self.total_foods_eaten // STAGE_PROGRESSION) + 1)
                if new_stage != self.stage and new_stage <= MAX_STAGE:
                    self.stage = new_stage
                    self.current_bg_color = STAGE_BACKGROUNDS.get(self.stage, STAGE_BACKGROUNDS[1])
                    self.canvas.config(bg=self.current_bg_color)
                    self.clear_background_effects()
                    self.create_background_effects()
                    self.show_stage_message()
            except Exception as e:
                print(f"Error in stage progression: {e}")
                # Fallback to safe state
                self.stage = min(MAX_STAGE, self.stage)
            
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
            self.bonus_food.delete()  # Delete all bonus food elements
            self.bonus_food = None
            self.update_display()
        else:
            # No food eaten, remove tail
            self.snake.coordinates.pop()

        self.draw_snake()
        
        # Animate background effects
        if self.running and not self.game_won:
            try:
                self.animate_background()
            except Exception as e:
                print(f"Error animating background: {e}")
        
        # Animate bonus food if it exists
        if self.bonus_food and self.running and not self.game_won:
            try:
                self.bonus_food.animate(self.canvas)
            except Exception as e:
                print(f"Error animating bonus food: {e}")
        
        # Continue game loop only if still running
        if self.running and not self.game_won:
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
        """Check if the snake collides with itself (excluding current head)"""
        # Don't check against the current head position, only body segments
        body_segments = self.snake.coordinates[1:] if len(self.snake.coordinates) > 1 else []
        return head in body_segments
    
    def get_elapsed_time(self):
        """Get formatted elapsed time since game start"""
        elapsed_seconds = int(time.time() - self.start_time)
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_timestamp_display(self):
        """Update timestamp in real-time every second"""
        if self.running and not self.game_won:
            try:
                # Get current display text and update only the timestamp part
                current_text = self.label.cget("text")
                
                # Find and replace the time portion
                import re
                elapsed_time = self.get_elapsed_time()
                # Replace the time pattern (MM:SS) in the current text
                updated_text = re.sub(r'Time: \d{2}:\d{2}', f'Time: {elapsed_time}', current_text)
                self.label.config(text=updated_text)
                
            except Exception as e:
                print(f"Error updating timestamp: {e}")
            
            # Schedule next update in 1 second
            self.root.after(1000, self.update_timestamp_display)
    
    def update_display(self):
        """Update score and stage display"""
        try:
            # Validate stage number
            if self.stage < 1 or self.stage > MAX_STAGE:
                print(f"Invalid stage: {self.stage}, resetting to 1")
                self.stage = 1
                
            stage_name = STAGE_NAMES.get(self.stage, "Unknown")
            multiplier = STAGE_MULTIPLIERS.get(self.stage, 1.0)
        except Exception as e:
            print(f"Error updating display: {e}")
            return
        
        # Calculate progress to next stage or victory
        if self.game_won:
            progress_text = " | VICTORY!"
            combo_text = ""
        elif self.total_foods_eaten >= VICTORY_FOODS:
            progress_text = " | READY TO WIN!"
            combo_text = ""
        else:
            foods_to_victory = VICTORY_FOODS - self.total_foods_eaten
            foods_in_current_stage = self.total_foods_eaten % STAGE_PROGRESSION
            foods_needed = STAGE_PROGRESSION - foods_in_current_stage
            
            combo_text = f" | COMBO x{self.combo_count}" if self.combo_count >= COMBO_THRESHOLD else ""
            
            if self.stage < MAX_STAGE:
                progress_text = f" | Next: {foods_needed} foods | Victory: {foods_to_victory} foods"
            else:
                progress_text = f" | MAX STAGE | Victory: {foods_to_victory} foods"
        
        # Create shorter label text to prevent window resizing (timestamp updated separately)
        base_text = f"Score: {self.score} | Stage: {self.stage} - {stage_name} (x{multiplier}) | Time: 00:00"
        if len(combo_text) > 0:
            base_text += combo_text
        
        # Get current elapsed time for this update
        elapsed_time = self.get_elapsed_time()
        base_text_with_time = f"Score: {self.score} | Stage: {self.stage} - {stage_name} (x{multiplier}) | Time: {elapsed_time}"
        
        # Truncate progress text if too long to prevent canvas width issues
        if len(base_text_with_time + progress_text) > 90:  # Slightly increased limit for timestamp
            if self.game_won:
                short_progress = " | VICTORY!"
            elif self.total_foods_eaten >= VICTORY_FOODS:
                short_progress = " | READY TO WIN!"
            else:
                foods_to_victory = VICTORY_FOODS - self.total_foods_eaten
                short_progress = f" | Victory in {foods_to_victory}"
            self.label.config(text=base_text_with_time + short_progress)
        else:
            self.label.config(text=base_text_with_time + progress_text)
    
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
    
    def show_victory_screen(self):
        """Show catchy victory celebration screen"""
        self.running = False
        
        # Create celebration background
        celebration_bg = self.canvas.create_rectangle(
            0, 0, GAME_WIDTH, GAME_HEIGHT,
            fill="#000033", outline="#FFD700", width=5
        )
        
        # Main victory title with glow effect
        title_glow = self.canvas.create_text(
            GAME_WIDTH // 2 + 2, GAME_HEIGHT // 2 - 48,
            font=('Arial', 36, 'bold'),
            fill="#FFD700",
            text="VICTORY!"
        )
        title_main = self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50,
            font=('Arial', 36, 'bold'),
            fill="#FFFFFF",
            text="VICTORY!"
        )
        
        # Victory message
        victory_msg = self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 - 10,
            font=('Arial', 18),
            fill="#00FF00",
            text="SNAKE MASTER ACHIEVED!\nYou conquered all 5 stages!"
        )
        
        # Score display with timestamp
        final_time = self.get_elapsed_time()
        score_display = self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 + 30,
            font=('Arial', 16, 'bold'),
            fill="#FFFF00",
            text=f"Final Score: {self.score} points\nFoods Eaten: {self.total_foods_eaten}\nSession Time: {final_time}\nStarted at: {self.session_start}"
        )
        
        # Restart instruction
        restart_msg = self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 + 70,
            font=('Arial', 12),
            fill="#CCCCCC",
            text="Press any key to play again!"
        )
        
        # Add celebration sparkles
        sparkles = []
        for _ in range(20):
            x = random.randint(50, GAME_WIDTH - 50)
            y = random.randint(50, GAME_HEIGHT - 50)
            sparkle = self.canvas.create_text(
                x, y, text=random.choice(["*", "+", ".", "o"]),
                fill=random.choice(["#FFD700", "#FFFFFF", "#FFFF00", "#FF69B4"]),
                font=("Arial", random.randint(12, 20))
            )
            sparkles.append(sparkle)
        
        # Animate sparkles
        def animate_sparkles(frame=0):
            if frame < 100:  # Animate for 100 frames
                for sparkle in sparkles:
                    if frame % 10 == 0:  # Every 10 frames
                        # Twinkle effect
                        current_color = self.canvas.itemcget(sparkle, "fill")
                        new_color = "#FFFFFF" if current_color != "#FFFFFF" else "#FFD700"
                        self.canvas.itemconfig(sparkle, fill=new_color)
                self.root.after(100, lambda: animate_sparkles(frame + 1))
        
        animate_sparkles()
        
        # Bind key to restart
        def restart_game(event):
            try:
                # Unbind the key event first
                self.root.unbind('<Key>')
                # Clear everything
                self.canvas.delete("all")
                # Reset game state
                self.reset()
                # Restart the game loop
                self.running = True
                # Restart timestamp updates
                self.update_timestamp_display()
                self.next_move()
            except Exception as e:
                print(f"Error restarting game: {e}")
        
        self.root.bind('<Key>', restart_game)
        self.root.focus_set()
    
    def clear_background_effects(self):
        """Clear all background elements"""
        try:
            for element in self.bg_elements:
                try:
                    self.canvas.delete(element)
                except Exception as e:
                    print(f"Error deleting background element: {e}")
            self.bg_elements = []
        except Exception as e:
            print(f"Error clearing background effects: {e}")
            self.bg_elements = []  # Reset to empty list
    
    def create_background_effects(self):
        """Create stage-specific background effects"""
        try:
            effects = STAGE_EFFECTS.get(self.stage, {})
            if self.stage not in STAGE_EFFECTS:
                print(f"Warning: No effects defined for stage {self.stage}")
                return
        except Exception as e:
            print(f"Error creating background effects: {e}")
            return
        
        if self.stage == 1:  # Starfield with depth
            # Distant stars
            for _ in range(30):
                x = random.randint(5, GAME_WIDTH - 5)
                y = random.randint(5, GAME_HEIGHT - 5)
                star = self.canvas.create_oval(x, y, x + 1, y + 1, fill="#CCCCCC", tags="background")
                self.bg_elements.append(star)
            # Medium stars
            for _ in range(15):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                star = self.canvas.create_oval(x, y, x + 2, y + 2, fill="#FFFFFF", tags="background")
                self.bg_elements.append(star)
            # Bright stars
            for _ in range(8):
                x = random.randint(15, GAME_WIDTH - 15)
                y = random.randint(15, GAME_HEIGHT - 15)
                # Star with glow
                glow = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#AAAAFF", tags="background")
                star = self.canvas.create_oval(x, y, x + 1, y + 1, fill="#FFFFFF", tags="background")
                self.bg_elements.extend([glow, star])
                
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
                crystal = self.canvas.create_oval(x, y, x + 6, y + 6, fill="#AA44AA", tags="background")
                self.bg_elements.append(crystal)
            # Sparkles
            for _ in range(20):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                sparkle = self.canvas.create_oval(x, y, x + 2, y + 2, fill="#FFAAFF", tags="background")
                self.bg_elements.append(sparkle)
                
        elif self.stage == 4:  # Jungle
            # Leaves
            for _ in range(effects.get("count", 40)):
                x = random.randint(10, GAME_WIDTH - 10)
                y = random.randint(10, GAME_HEIGHT - 10)
                leaf = self.canvas.create_oval(x, y, x + 4, y + 6, fill="#44AA44", tags="background")
                self.bg_elements.append(leaf)
            # Vine patterns
            for i in range(3):
                x = i * 200 + 100
                vine = self.canvas.create_line(x, 0, x + 50, GAME_HEIGHT, fill="#226622", width=3, tags="background")
                self.bg_elements.append(vine)
                
        elif self.stage == 5:  # Desert
            try:
                # Sand dunes
                for i in range(4):
                    x = i * 150
                    if x + 200 <= GAME_WIDTH:  # Ensure dune fits in canvas
                        dune = self.canvas.create_arc(x, GAME_HEIGHT - 60, x + 200, GAME_HEIGHT, start=0, extent=180, outline="#AA8844", width=2, tags="background")
                        self.bg_elements.append(dune)
                # Sand particles
                particle_count = min(35, effects.get("count", 35))  # Limit particles
                for _ in range(particle_count):
                    x = random.randint(10, GAME_WIDTH - 10)
                    y = random.randint(10, GAME_HEIGHT - 10)
                    sand = self.canvas.create_oval(x, y, x + 2, y + 2, fill="#CCAA66", outline="#CCAA66", tags="background")
                    self.bg_elements.append(sand)
            except Exception as e:
                print(f"Error creating desert effects: {e}")
    
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
        """Calculate current game speed based on foods eaten for realistic progression"""
        # Use foods eaten instead of score for more predictable speed progression
        foods_eaten = self.total_foods_eaten
        
        if foods_eaten <= 10:
            return SPEED  # Normal speed for first 10 foods
        elif foods_eaten <= 20:
            # Gradual speed increase: 100ms -> 90ms over 10 foods
            return max(90, SPEED - (foods_eaten - 10) * 1)
        elif foods_eaten <= 40:
            # Moderate speed increase: 90ms -> 80ms over 20 foods  
            # Use integer division to avoid float results
            return max(80, 90 - (foods_eaten - 20) // 2)
        elif foods_eaten <= 60:
            # Slower progression: 80ms -> 75ms over 20 foods
            # Use integer division to avoid float results  
            return max(75, 80 - (foods_eaten - 40) // 4)
        else:
            # Cap at reasonable maximum speed
            return 75  # Never faster than 75ms (still playable)

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
    
    # Set window icon and properties
    try:
        root.iconname("Snake Game")
    except:
        pass  # Icon setting might fail on some systems
    
    game = SnakeGame(root)
    
    # Make sure window is focused
    root.focus_force()
    root.lift()
    
    root.mainloop()
