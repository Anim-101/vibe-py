import tkinter as tk
import random

# Game configuration
GAME_WIDTH = 600
GAME_HEIGHT = 400
SPEED = 100  # Milliseconds between moves
SPACE_SIZE = 20
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BG_COLOR = "#000000"

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
        self.square = self.canvas.create_oval(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=FOOD_COLOR, tag="food"
        )
        
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game (Tkinter)")
        self.score = 0

        self.label = tk.Label(root, text=f"Score: {self.score}", font=('consolas', 20))
        self.label.pack()

        self.canvas = tk.Canvas(root, bg=BG_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
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
        self.score = 0
        self.label.config(text=f"Score: {self.score}")

    def draw_snake(self):
        for square in self.snake.squares:
            self.canvas.delete(square)
        self.snake.squares = []
        for x, y in self.snake.coordinates:
            square = self.canvas.create_rectangle(
                x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake"
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

        new_head = [x, y]

        if self.check_collisions(new_head):
            self.game_over()
            return

        self.snake.coordinates.insert(0, new_head)

        # Food collision
        if x == self.food.x and y == self.food.y:
            self.score += 1
            self.label.config(text=f"Score: {self.score}")
            self.canvas.delete(self.food.square)
            self.food.place_new(self.snake)
        else:
            self.snake.coordinates.pop()

        self.draw_snake()
        self.root.after(SPEED, self.next_move)

    def change_direction(self, new_direction):
        opposites = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
        if opposites[new_direction] != self.direction:
            self.direction = new_direction

    def check_collisions(self, head):
        x, y = head
        if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
            return True
        if head in self.snake.coordinates:
            return True
        return False

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
