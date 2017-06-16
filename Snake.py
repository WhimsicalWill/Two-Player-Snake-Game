from graphics import *
import time
from pynput import keyboard
import random
# 0, 0 is in the top left of the screen


SCR_WIDTH, SCR_HEIGHT = 800, 800
win = GraphWin("Snake", SCR_WIDTH, SCR_HEIGHT)

NUM_BLOCKS = 25
SNAKE_LENGTH = 4

BLOCK_WIDTH = SCR_WIDTH / NUM_BLOCKS
BLOCK_HEIGHT = SCR_HEIGHT / NUM_BLOCKS

# 1 - right 2 - up 3 - left 4 - down


class Snake:
    def create_snake(self, y):
        new_snake = []
        for i in range(self.length):
            new_snake.append([self.length - 1 - i, y, 1])
        return new_snake

    # make snake class with turtle_direction as a parameter
    def __init__(self, y, snake_length):
        # When the user turns, the turn list appends the position that the
        # occurs so that the snake doesnt have to turn all at once
        self.turns = []
        # Contains every single block of the snake. Each block has an x,
        # y, and direction value
        self.length = snake_length
        # Create snake at a specific y coordinate
        self.pos = self.create_snake(y)
        self.has_eaten_food = False
        self.head = self.pos[0]

    # Changes a given block of the snake's direction
    def set_direction(self, num_block, direction):
        self.pos[num_block][2] = direction
        if self.pos[num_block][2] == 0:
            self.pos[num_block][2] = 4
        elif self.pos[num_block][2] == 5:
            self.pos[num_block][2] = 1

    # Adds a turn in a given direction, at a given position
    def add_turn(self, direction):
        # If the directions contradict each other (e.g. trying to go left when moving right)
        if abs(self.head[2] - direction) == 2:
            return
        turn_pos = self.head[:2]
        turn_pos.append(direction)
        self.turns.append(turn_pos)

    def move_forward(self):
        # Make a copy of the last block of the snake in case we need to increase size
        tail = self.pos[len(self.pos) - 1][:]

        # Move every block forward in the correct direction
        for block in self.pos:
            if block[2] == 1:
                block[0] += 1
            elif block[2] == 2:
                block[1] -= 1
            elif block[2] == 3:
                block[0] -= 1
            elif block[2] == 4:
                block[1] += 1

            # If the player goes beyond the borders
            # Minus 1 because there are 20 blocks, but the right most one is at position 19 (0 indexed)
            if block[0] > NUM_BLOCKS - 1:
                block[0] = 0
            elif block[0] < 0:
                block[0] = NUM_BLOCKS - 1
            elif block[1] > NUM_BLOCKS - 1:
                block[1] = 0
            elif block[1] < 0:
                block[1] = NUM_BLOCKS - 1

        if self.has_eaten_food:
            self.has_eaten_food = False
            self.pos.append(tail)

    def update_direction(self):
        # Turns must be deleted after they have been processed
        def delete_turns(indexes, turn_list):
            for k in range(len(indexes)):
                # Delete the largest index so it doesnt mess up the others
                del turn_list[indexes.index(max(indexes))]
                del indexes[indexes.index(max(indexes))]

        completed_turns = []
        # The scheduled left turns
        for i in range(len(self.turns)):
            # The positions of each block in the snake
            for j in range(len(self.pos)):
                if self.turns[i][:2] == self.pos[j][:2]:
                    self.set_direction(j, self.turns[i][2])
                    if j == len(self.pos) - 1:
                        # Store the indexes of the turns that need to be deleted
                        completed_turns.append(i)

        delete_turns(completed_turns, self.turns)


class Food:
    def spawn(self):
        self.pos = [random.randrange(NUM_BLOCKS), random.randrange(NUM_BLOCKS)]

    def __init__(self):
        self.pos = []
        self.spawn()


def draw_foods(foods):
        # Clear the canvas before drawing each frame
        win.delete('all')
        for foo in foods:
            coords = [(SCR_HEIGHT / NUM_BLOCKS) * i for i in foo.pos]
            rect = Rectangle(Point(coords[0], coords[1]), Point(coords[0] + BLOCK_WIDTH, coords[1] + BLOCK_HEIGHT))
            rect.setFill("yellow")
            rect.draw(win)


def end_game(message):
        while True:
            time.sleep(2)
            exit(message)


# Draw both snakes
def draw_snakes(snakes):
        for i in range(len(snakes)):
            coords = []
            # i[0:2] gets only the coordinates and ignores direction
            for j in snakes[i].pos:
                coords.append([(SCR_HEIGHT / NUM_BLOCKS) * k for k in j[0:2]])
            for l in coords:
                rect = Rectangle(Point(l[0], l[1]), Point(l[0] + BLOCK_WIDTH, l[1] + BLOCK_HEIGHT))

                if i == 1:
                    rect.setFill("red")
                else:
                    rect.setFill("blue")
                rect.draw(win)


# Test for snake collisions
def test_collision(snake1, snake2, foods):
    head = snake1.pos[0]
    red_loss = False
    blue_loss = False
    # Test for collisions within snake1
    for i in range(1, len(snake1.pos)):
        if head[0:2] == snake1.pos[i][0:2]:
            blue_loss = True

    # Test for collisions from snake1 to snake2
    for i in range(len(snake2.pos)):
        if head[0:2] == snake2.pos[i][0:2]:
            blue_loss = True

    # Test for collisions from snake1 head to the food
    for i in foods:
        if head[0:2] == i.pos:
            snake1.has_eaten_food = True
            i.spawn()
            # There can only be one collision, so continue if we find one
            continue

    head = snake2.pos[0]
    # Test for collisions within snake2
    for i in range(1, len(snake2.pos)):
        if head[0:2] == snake2.pos[i][0:2]:
            red_loss = True

    # Test for collisions from snake2 to snake1
    for i in range(len(snake1.pos)):
        if head[0:2] == snake1.pos[i][0:2]:
            red_loss = True

    # Test for collisions from snake2 head to the food
    for i in foods:
        if head[0:2] == i.pos:
            snake2.has_eaten_food = True
            i.spawn()
            # There can only be one collision, so continue if we find one
            continue

    # If both players lose in the same frame (e.g. head on collision), tie the game
    if red_loss and blue_loss:
        end_game("Game Over: Tie")
    elif red_loss:
        end_game("Game Over: Blue Wins")
    elif blue_loss:
        end_game("Game Over: Red Wins")


# Main game loop
def main(snake1, snake2):
    while True:
        # Draw food before snakes so that snakes appear over food on the z axis
        draw_foods([food1, food2])
        # Draw both in the same function, because we don't want to clear canvas between draws
        draw_snakes([snake1, snake2])
        test_collision(snake1, snake2, [food1, food2])
        snake1.update_direction()
        snake2.update_direction()
        snake1.move_forward()
        snake2.move_forward()
        time.sleep(0.1)


def on_press(key):
    try:
        k = key.char
    except:
        k = key.name
    if k == "right":
        sn1.add_turn(1)
    if k == "up":
        sn1.add_turn(2)
    if k == "left":
        sn1.add_turn(3)
    if k == "down":
        sn1.add_turn(4)
    if k == "d":
        sn2.add_turn(1)
    if k == "w":
        sn2.add_turn(2)
    if k == "a":
        sn2.add_turn(3)
    if k == "s":
        sn2.add_turn(4)

sn1 = Snake(4, SNAKE_LENGTH)
sn2 = Snake(15, SNAKE_LENGTH)
food1 = Food()
food2 = Food()
lis = keyboard.Listener(on_press=on_press)
lis.start()  # start to listen on a separate thread
main(sn1, sn2)
