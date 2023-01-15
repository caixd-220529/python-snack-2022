import pygame
import random
import pygame.locals
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.ticker import MaxNLocator
import datetime

print(pygame.font.get_fonts())

TITLE = '计创 蔡希迪 202130430010'
WIDTH = 800
HEIGHT = 600
SNAKE_SIZE = 20
GRAPH_Y = 100
str2direction = {
    'right': (SNAKE_SIZE, 0),
    'left': (-SNAKE_SIZE, 0),
    'up': (0, -SNAKE_SIZE),
    'down': (0, SNAKE_SIZE),
}
game_state = False
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
time_begin = -1
time_end = -1
user_id = -1
temp_id = 1
today = datetime.date.today()
record_path = 'record/record'
KEY_DIRECTION_DICT = {
    119: 'up',  # W
    115: 'down',  # S
    97: 'left',  # A
    100: 'right',  # D
}
have_stored_the_score = False
user_id2str = {
    1: '草蛇',
    2: '眼睛蛇',
    3: '银环蛇'
}


class Point:
    def __init__(self, x, y=0):
        if type(x) == Point:
            self.x = x.x
            self.y = x.y
            return
        self.x = x
        self.y = y
        return

    def move(self, moving_direction):
        self.x += moving_direction[0]
        self.y += moving_direction[1]

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'POINT({self.x}, {self.y})'


class Snake:
    def __init__(self):
        self.possible_location = []
        self.current_direction = 'right'
        self.speed = 8
        self.score = 0
        self.next_food = Point(0, 0)

        for i in range(2, int(WIDTH / SNAKE_SIZE) - 2):
            for j in range(2, int(HEIGHT / SNAKE_SIZE) - 2):
                self.possible_location.append((i, j))
        self.snake_body = [Point(1 * SNAKE_SIZE, 2 * SNAKE_SIZE),
                           Point(2 * SNAKE_SIZE, 2 * SNAKE_SIZE),
                           Point(3 * SNAKE_SIZE, 2 * SNAKE_SIZE), ]
        head = Point(self.snake_body[-1].x, self.snake_body[-1].y)
        self.snake_head = head
        self.get_food_position()

    def get_food_position(self):
        possible = [i for i in self.possible_location if Point(i[0]*20, i[1]*20) not in self.snake_body]
        """print('------------')
        print(self.possible_location)  # (2, 2), (2, 3)
        print(self.snake_body)
        print(len(possible))
        print('------------')"""
        # possible列表中的元素是一个个元组，元组是可能的x, y坐标(x, y)
        food = random.sample(possible, 1)
        food = food[0]
        self.next_food.x = food[0] * 20
        self.next_food.y = food[1] * 20

    def snack_move(self):
        head = Point(self.snake_body[-1].x, self.snake_body[-1].y)
        self.snake_head = head
        self.snake_head.move(str2direction[self.current_direction])
        if not self.alive(self.snake_head):
            return False
        self.snake_body.append(self.snake_head)
        if (self.snake_head.x == self.next_food.x) and (self.snake_head.y == self.next_food.y):
            self.score += 1
            if self.score % 5 == 0:
                self.speed += 2
            self.get_food_position()
        else:
            self.snake_body.pop(0)
        return True

    def alive(self, head):
        return 0 < head.x < WIDTH - SNAKE_SIZE and 0 < head.y < HEIGHT - SNAKE_SIZE and head not in self.snake_body


def press(events, snake, screen, last_time_score):
    global have_stored_the_score
    for event in events:
        if event.type == pygame.locals.QUIT:
            exit()

        if event.type == pygame.locals.KEYDOWN:
            if event.key == 13:
                global game_state, time_begin
                game_state = True
                time_begin = time.time()
                have_stored_the_score = False

            if not game_state and event.key == 121 and last_time_score >= 0 and not have_stored_the_score:
                have_stored_the_score = True
                tips_font = pygame.font.SysFont('SimSun', 24)
                pygame.draw.rect(screen, (255, 255, 255), [700, 0, 400, 50], 0)
                screen.blit(tips_font.render('成绩已保存', True, (0, 0, 0), (255, 255, 255)), (600, 0))
                with open(record_path, 'a') as record_txt:
                    record_txt.write(f' {last_time_score}')
                draw_graph(screen)
                pygame.display.update()

            if not game_state and event.key == 99:
                with open(record_path, 'r') as f:
                    if f.read() == '':
                        pass
                    else:
                        with open(record_path, 'w') as record_txt:
                            pass
                        pygame.draw.rect(screen, (255, 255, 255), [0, GRAPH_Y, 1000, 1000], 0)
                        pygame.draw.rect(screen, (255, 255, 255), [600, 0, 200, 50], 0)
                        screen.blit(pygame.font.SysFont('SimSun', 24).render('已经成功清除所有历史游戏记录!', True,
                                                                             (0, 0, 0), (255, 255, 255)), (220, 100))
                pygame.display.update()

            if game_state and event.key in KEY_DIRECTION_DICT:
                return direction_check(snake.current_direction,
                                       KEY_DIRECTION_DICT[event.key])


def draw_score(screen, score, position):
    tips_font = pygame.font.SysFont('SimSun', 20)
    screen.blit(
        tips_font.render('当前分数: {}'.format(score), True, (0, 0, 0),
                         (255, 255, 255)), position)


def draw_graph(screen):
    with open(record_path, 'r') as record_txt:
        history = record_txt.read().split(' ')
        if len(history) == 1:
            return
        history.pop(0)
        x_index = []
        for i in range(len(history)):
            if not history[i].isnumeric():
                with open(record_path, 'w') as f:
                    pass
                return
            history[i] = int(history[i])
            x_index.append(i + 1)
        fig, ax = plt.subplots()
        plt.plot(x_index, history)
        ax.set_xlabel('次数')
        ax.set_ylabel('成绩')
        ax.set_title(f'{user_id2str[user_id]}的过往成绩')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        # plt.ylim(ymin=-0.5)
        for a, b in zip(x_index, history):
            plt.text(a, b, (a, b), ha='center', va='bottom', fontsize=10)
        plt.savefig('./image/record.png')
        history_img = pygame.image.load("image/record.png").convert()
        screen.blit(history_img, (80, GRAPH_Y))
        data = np.array(history)
        screen.blit(pygame.font.SysFont('SimSun', 24).render(f'历史成绩的方差为{data.var():.2f}, '
                                                             f'历史成绩的均值为{data.mean():.2f},'
                                                             f'历史最高成绩为{data.max()}分', True,
                                                             (0, 0, 0), (255, 255, 255)), (0, 600))


def draw_account_graph(screen):
    global temp_id
    record_1 = []
    record_2 = []
    record_3 = []
    x_1 = []
    x_2 = []
    x_3 = []
    all_record = [record_1, record_2, record_3]
    all_x = [x_1, x_2, x_3]
    all_color = ['green', 'black', 'blue']
    id_name = ['草蛇', '眼镜蛇', '银环蛇']
    for i in range(1, 4):
        with open(f'record/record_{i}.txt', 'r') as f:
            temp = f.read().split(' ')
            if len(temp) != 1:
                temp.pop(0)
                for index in range(len(temp)):
                    if not temp[index].isnumeric():
                        with open(record_path, 'w') as k:
                            pass
                        return
                    all_record[i - 1].append(int(temp[index]))
                    all_x[i - 1].append(index + 1)
    fig, ax = plt.subplots()
    ax.set_xlabel('次数')
    ax.set_ylabel('成绩')
    ax.set_title('所有人过往成绩')
    for i in range(3):
        if temp_id - 1 != i:
            plt.plot(all_x[i], all_record[i], color=all_color[i], linestyle=':', label=id_name[i])
        else:
            plt.plot(all_x[i], all_record[i], color=all_color[i], label=id_name[i])
    plt.legend()
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    for i in range(3):
        for a, b in zip(all_x[i], all_record[i]):
            plt.text(a, b, (a, b), ha='center', va='bottom', fontsize=10)
    plt.savefig('./image/all_record.png')
    history_img = pygame.image.load("image/all_record.png").convert()
    screen.blit(history_img, (80, GRAPH_Y))
    data = np.array(all_record[temp_id - 1])
    if len(all_record[temp_id-1]) == 0:
        pygame.draw.rect(screen, [255, 255, 255], [0, 600, 1000, 1000], 0)
        screen.blit(pygame.font.SysFont('SimSun', 24).render(f'没有查询到{user_id2str[temp_id]}的游戏记录!', True, (0, 0, 0), (255, 255, 255)), (0, 600))
        return
    screen.blit(pygame.font.SysFont('SimSun', 24).render(f'历史成绩的方差为{data.var():.2f}, '
                                                         f'历史成绩的均值为{data.mean():.2f},'
                                                         f'历史最高成绩为{data.max()}分', True,
                                                         (0, 0, 0), (255, 255, 255)), (0, 600))


def direction_check(move_direction, change_direction):
    directions = [['up', 'down'], ['left', 'right']]
    if move_direction in directions[0] and change_direction in directions[1]:
        return change_direction
    elif move_direction in directions[1] and change_direction in directions[0]:
        return change_direction
    return move_direction


def print_board(screen, snake):
    pygame.draw.rect(screen, (240, 248, 255), [0, 0, 800, 600], 0)
    side_img = pygame.image.load("image/side.png").convert()
    for i in range(WIDTH // SNAKE_SIZE):
        screen.blit(side_img, (i * 20, 0))
        screen.blit(side_img, (i * 20, HEIGHT - 20))
    for i in range(HEIGHT // SNAKE_SIZE):
        screen.blit(side_img, (0, i * 20))
        screen.blit(side_img, (WIDTH - 20, i * 20))


def choose_account(screen, fps_clock):
    current = 1
    position_1 = 25
    position_2 = 50
    position_3 = 75
    choose_rgb = (128, 0, 128)
    global user_id, record_path, temp_id
    temp_id = 1
    screen.blit(pygame.font.SysFont('SimSun', 24).render('请通过w和s选择账号，按Enter确定', True, (0, 0, 0), (255, 255, 255)),
                (230, 0))
    show_user_name(screen, '草蛇', choose_rgb, position_1)
    show_user_name(screen, '眼睛蛇', (0, 0, 0), position_2)
    show_user_name(screen, '银环蛇', (0, 0, 0), position_3)
    draw_account_graph(screen)
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.locals.QUIT:
                exit()
            if event.type == pygame.locals.KEYDOWN:
                if event.key == 115:
                    current = current + 1 if current != 3 else 3
                    temp_id = current
                    draw_account_graph(screen)
                if event.key == 119:
                    current = current - 1 if current != 1 else 1
                    temp_id = current
                    draw_account_graph(screen)
                if event.key == 13:
                    user_id = current
                    break
            if current == 1:
                show_user_name(screen, '草蛇', choose_rgb, position_1)
                show_user_name(screen, '眼睛蛇', (0, 0, 0), position_2)
                show_user_name(screen, '银环蛇', (0, 0, 0), position_3)
            elif current == 2:
                show_user_name(screen, '草蛇', (0, 0, 0), position_1)
                show_user_name(screen, '眼睛蛇', choose_rgb, position_2)
                show_user_name(screen, '银环蛇', (0, 0, 0), position_3)
            else:
                show_user_name(screen, '草蛇', (0, 0, 0), position_1)
                show_user_name(screen, '眼睛蛇', (0, 0, 0), position_2)
                show_user_name(screen, '银环蛇', choose_rgb, position_3)
        if user_id != -1:
            record_path = record_path + '_' + str(user_id) + '.txt'
            print(record_path)
            break
        pygame.display.update()
        fps_clock.tick(30)


def show_user_name(screen, name, color, y_pos):
    screen.blit(pygame.font.SysFont('SimSun', 24).render(name, True, color, (255, 255, 255)), (350, y_pos))


def font_setting():
    global time_end, time_begin, user_id
    user_name = user_id2str[user_id]
    title_font = pygame.font.SysFont('SimSun', 32)
    welcome_words = title_font.render("一起来玩贪吃蛇！", True, (0, 0, 0),
                                      (255, 255, 255))

    tips_font = pygame.font.SysFont('SimSun', 24)
    start_game_words = tips_font.render(f'单击 Enter 来开始游戏, 通过wasd来{user_name}的控制', True,
                                        (0, 0, 0), (255, 255, 255))

    game_over_font = pygame.font.SysFont('Times New Roman', 32)
    game_over_words = game_over_font.render('GAME OVER', True, (255, 0, 0),
                                            (255, 255, 255))
    return {
        'welcome': welcome_words,
        'start': start_game_words,
        'game_over': game_over_words,
    }


def main():
    global game_state, have_stored_the_score, user_id
    pygame.init()
    fps_clock = pygame.time.Clock()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 40))
    screen.fill((255, 255, 255))
    choose_account(screen, fps_clock)
    screen.fill((255, 255, 255))
    draw_graph(screen)
    fonts = font_setting()  # type(fonts): dictionary
    screen.blit(fonts['welcome'], (275, 0))
    screen.blit(fonts['start'], (150, 50))
    with open(record_path, 'r') as record_txt:
        history = record_txt.read().split(' ')
        if len(history) != 1:
            screen.blit(pygame.font.SysFont('SimSun', 24).render('单击 c 来该账号所有历史游戏记录', True,
                                                                 (0, 0, 0), (255, 255, 255)), (220, 100))
    snake = Snake()
    last_time_score = -1
    while True:
        events = pygame.event.get()
        new_direction = press(events, snake, screen, last_time_score)
        if game_state:
            have_valid_score = True
            if new_direction:
                snake.current_direction = new_direction
            screen.fill((255, 255, 255))
            if not snake.snack_move():
                global time_end, time_begin
                time_end = time.time()
                screen.blit(fonts['game_over'], (310, 50))
                tips_font = pygame.font.SysFont('SimSun', 24)
                screen.blit(tips_font.render('你的最终分数为: {}'.format(snake.score), True, (0, 0, 0), (255, 255, 255)),
                            (300, 150))
                screen.blit(tips_font.render('单击y记录本次游戏成绩', True, (0, 0, 0), (255, 255, 255)), (0, 0))
                screen.blit(tips_font.render(f'单击c清除{user_id2str[user_id]}的所有历史游戏记录',
                                             True, (0, 0, 0), (255, 255, 255)), (0, 24))
                screen.blit(tips_font.render('单击 Enter 开始游戏', True, (0, 0, 0), (255, 255, 255)), (0, 48))
                screen.blit(pygame.font.SysFont('SimSun', 24).render(f'存活时间: {time_end - time_begin:.2f}s',
                                                                     True, (0, 0, 0), (255, 255, 255)), (600, 0))
                draw_graph(screen)
                last_time_score = snake.score
                snake = Snake()
                game_state = False

            else:
                print_board(screen, snake)
                draw_score(screen, snake.score, (0, HEIGHT))
                instructions_font = pygame.font.SysFont('SimSun', 20)
                instructions = instructions_font.render('通过wasd来控制小蛇的移动', True,
                                                        (0, 0, 0), (255, 255, 255))
                screen.blit(instructions, (0, HEIGHT + 20))

                head_img = pygame.image.load(f"image/{snake.current_direction}_head.png").convert()
                body_img = pygame.image.load("image/body.png").convert()
                for i in range(len(snake.snake_body) - 1):
                    screen.blit(body_img, (snake.snake_body[i].x, snake.snake_body[i].y))
                screen.blit(head_img, (snake.snake_body[len(snake.snake_body) - 1].x,
                                       snake.snake_body[len(snake.snake_body) - 1].y))
                pygame.draw.circle(screen, (255, 0, 0),
                                   (snake.next_food.x + 10, snake.next_food.y + 10), 10)

        pygame.display.update()
        fps_clock.tick(snake.speed)


if __name__ == '__main__':
    main()
