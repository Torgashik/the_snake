from random import randint
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480  # Ширина и высота экрана
GRID_SIZE = 20  # Размер клетки в пикселях
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE  # Ширина сетки в клетках
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # Высота сетки в клетках
UP = (0, -1)  # Направление вверх
DOWN = (0, 1)  # Направление вниз
LEFT = (-1, 0)  # Направление влево
RIGHT = (1, 0)  # Направление вправо
BOARD_BACKGROUND_COLOR = (0, 0, 0)  # Цвет фона игрового поля
BORDER_COLOR = (93, 216, 228)  # Цвет границы клеток
APPLE_COLOR = (255, 0, 0)  # Цвет яблока
SNAKE_COLOR = (0, 255, 0)  # Цвет змейки
ROCK_COLOR = (128, 128, 128)  # Цвет камня
SPEED = 10  # Скорость игры

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32
)  # Установка размера экрана
pygame.display.set_caption("Змейка")  # Установка заголовка окна
clock = pygame.time.Clock()  # Создание объекта часов для управления частотой кадров


class GameObject:
    """Класс, представляющий игровой объект."""

    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
        """Инициализация игрового объекта.

        Аргументы:
            grid_width (int): Ширина сетки в клетках.
            grid_height (int): Высота сетки в клетках.
        """
        self.position = ((grid_width // 2) * GRID_SIZE, (grid_height // 2) * GRID_SIZE)
        self.body_color = None

    def draw(self):
        """Метод для рисования объекта на экране. (для наследуемых объектов)"""
        pass


class Snake(GameObject):
    """Класс, представляющий змейку."""

    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
        """Инициализация змейки.

        Аргументы:
            grid_width (int): Ширина сетки в клетках.
            grid_height (int): Высота сетки в клетках.
        """
        super().__init__(grid_width, grid_height)
        self.length = 1  # Начальная длина змейки
        self.positions = [self.position]  # Начальная позиция головы змейки
        self.direction = RIGHT  # Начальное направление
        self.next_direction = None  # Направление, в которое змейка должна двигаться
        self.body_color = SNAKE_COLOR  # Цвет тела змейки

    def update_direction(self):
        """Обновление направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещение змейки в текущем направлении."""
        head_x, head_y = self.get_head_position()

        if self.direction == RIGHT:
            new_head = (head_x + GRID_SIZE, head_y)
        elif self.direction == LEFT:
            new_head = (head_x - GRID_SIZE, head_y)
        elif self.direction == UP:
            new_head = (head_x, head_y - GRID_SIZE)
        elif self.direction == DOWN:
            new_head = (head_x, head_y + GRID_SIZE)

        # Обеспечение зацикливания на экране
        new_head = (new_head[0] % SCREEN_WIDTH, new_head[1] % SCREEN_HEIGHT)

        self.positions.insert(
            0, new_head
        )  # Добавление новой головы в начало списка позиций

        if len(self.positions) > self.length:
            self.last = self.positions.pop()  # Удаление последней позиции

    def draw(self):
        """Рисование змейки на экране."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)  # Рисуем тело змейки
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)  # Рисуем границу клетки

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)  # Рисуем голову змейки
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)  # Рисуем границу головы

        if hasattr(self, "last"):
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(
                screen, BOARD_BACKGROUND_COLOR, last_rect
            )  # Стираем последнюю позицию

    def get_head_position(self):
        """Получение текущей позиции головы змейки.

        Возвращает:
            tuple: Координаты головы змейки.
        """
        return self.positions[0]

    def reset(self):
        """Сброс змейки к начальному состоянию."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None

    def is_position_inside_snake(self, position):
        """Проверка, находится ли заданная позиция внутри тела змейки.

        Аргументы:
            position (tuple): Координаты позиции для проверки.

        Возвращает:
            bool: True, если позиция находится внутри тела змейки, иначе False.
        """
        return position in self.positions


class Apple(GameObject):
    """Класс, представляющий яблоко."""

    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT, snake=None):
        """Инициализация яблока.

        Аргументы:
            grid_width (int): Ширина сетки в клетках.
            grid_height (int): Высота сетки в клетках.
            snake (Snake): Объект змейки, чтобы не спавнить яблоко внутри змейки.
        """
        super().__init__(grid_width, grid_height)
        self.body_color = APPLE_COLOR  # Цвет яблока
        self.snake = snake  # Ссылка на объект змейки
        self.randomize_position(grid_width, grid_height)  # Установка случайной позиции

    def randomize_position(self, grid_width, grid_height):
        """Установка случайной позиции яблока, избегая пересечения со змейкой.

        Аргументы:
            grid_width (int): Ширина сетки в клетках.
            grid_height (int): Высота сетки в клетках.
        """
        while True:
            self.position = (
                randint(0, grid_width - 1) * GRID_SIZE,
                randint(0, grid_height - 1) * GRID_SIZE,
            )
            if not self.snake or not self.snake.is_position_inside_snake(self.position):
                break

    def draw(self):
        """Рисование яблока на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)  # Рисуем яблоко
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)  # Рисуем границу яблока


class Rock(GameObject):
    """Класс, представляющий камень."""

    def __init__(self, grid_width, grid_height):
        """Инициализация камня.

        Аргументы:
            grid_width (int): Ширина сетки в клетках.
            grid_height (int): Высота сетки в клетках.
        """
        super().__init__(grid_width, grid_height)
        self.body_color = ROCK_COLOR  # Цвет камня
        self.randomize_position(grid_width, grid_height)  # Установка случайной позиции

    def randomize_position(self, grid_width, grid_height):
        """Установка случайной позиции камня.

        Аргументы:
            grid_width (int): Ширина сетки в клетках.
            grid_height (int): Высота сетки в клетках.
        """
        while True:
            self.position = (
                randint(0, grid_width - 1) * GRID_SIZE,
                randint(0, grid_height - 1) * GRID_SIZE,
            )
            break

    def draw(self):
        """Рисование камня на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)  # Рисуем камень
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)  # Рисуем границу камня


def handle_keys(game_object):
    """Обработка нажатий клавиш для управления игровым объектом.

    Аргументы:
        game_object (GameObject): Игровой объект, который нужно управлять (например, змейка).
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    pygame.init()  # Инициализация Pygame

    snake_obj = Snake(GRID_WIDTH, GRID_HEIGHT)  # Создание объекта змейки
    apple_obj = Apple(GRID_WIDTH, GRID_HEIGHT, snake_obj)  # Создание объекта яблока
    rock_obj = Rock(GRID_WIDTH, GRID_HEIGHT)  # Создание объекта камня

    while True:
        clock.tick(SPEED)  # Ограничение частоты кадров
        handle_keys(snake_obj)  # Обработка нажатий клавиш
        snake_obj.update_direction()  # Обновление направления змейки
        snake_obj.move()  # Перемещение змейки

        # Проверка на столкновение с яблоком
        if snake_obj.get_head_position() == apple_obj.position:
            snake_obj.length += 1  # Увеличение длины змейки
            apple_obj.randomize_position(
                GRID_WIDTH, GRID_HEIGHT
            )  # Установка новой позиции яблока

        # Проверка на столкновение со своим телом
        if snake_obj.get_head_position() in snake_obj.positions[1:]:
            snake_obj.reset()  # Сброс змейки

        # Проверка на столкновение с камнем
        if snake_obj.get_head_position() == rock_obj.position:
            snake_obj.reset()  # Сброс змейки

        screen.fill(BOARD_BACKGROUND_COLOR)  # Очистка экрана
        snake_obj.draw()  # Рисование змейки
        apple_obj.draw()  # Рисование яблока
        rock_obj.draw()  # Рисование камня
        pygame.display.update()  # Обновление экрана


if __name__ == "__main__":
    main()  # Запуск основной функции
