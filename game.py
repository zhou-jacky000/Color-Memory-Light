import pygame
import random
from moviepy.editor import VideoFileClip
import os 
import sys

# 用於找到打包後的資源路徑 
def resource_path(relative_path): 
    try: 
        # PyInstaller 創建臨時文件夾，將路径存储在 _MEIPASS 中 
        base_path = sys._MEIPASS
    except Exception: 
        base_path = os.path.abspath(".") 
    return os.path.join(base_path, relative_path) 

video_path = resource_path(r"C:\個人資料\game\istockphoto.mp4") # 載入背景影片 
font_path = resource_path("Qualy/Qualy/Qualy-Bold-2.ttf")
# 確保在程式中引用正確的路徑 
font = pygame.font.Font(font_path, 20)
clip = VideoFileClip(video_path)

# 初始化 pygame
pygame.init()

# 視窗設置
WIDTH, HEIGHT = 600, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("記憶遊戲")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0)  # 正常高亮顏色
ERROR_HIGHLIGHT = (255, 0, 0)  # 答錯時顯示的紅色高亮
BUTTON_COLOR = (100, 200, 255)
BUTTON_SHADOW_COLOR = (70, 140, 180)
TEXT_COLOR = (255, 0, 0)

# 字體設置
try:
    font = pygame.font.Font(font_path, 20)
except FileNotFoundError:
    font = pygame.font.SysFont("Microsoft JhengHei", 40)

# 分區設置
TOP_AREA_HEIGHT = HEIGHT // 10
GRID_SIZE = 3
CELL_SIZE = (HEIGHT - TOP_AREA_HEIGHT) // GRID_SIZE

# 遊戲狀態
sequence = []
player_sequence = []
level = 1
running = True
game_started = False
showing_sequence = False
player_turn = False
leaderboard = []
game_over = False #用來看遊戲狀態

# 載入背景影片
clip = VideoFileClip(video_path)  # 替換為流星背景影片的路徑
clip = clip.resize((WIDTH, HEIGHT))  # 調整影片大小以符合窗口
clip_frames = clip.iter_frames(fps=240, dtype="uint8")

# 隨機生成序列
def generate_sequence(level):
    return [random.randint(0, 8) for _ in range(level)]

# 顯示方框並高亮指定的序列，增加陰影效果
def display_grid(highlight_cells=[], highlight_color=HIGHLIGHT):
    margin = 10
    shadow_offset = 5  # 陰影的偏移量
    shadow_color = (50, 50, 50)  # 陰影顏色
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x, y = j * CELL_SIZE + margin, i * CELL_SIZE + TOP_AREA_HEIGHT + margin
            rect = pygame.Rect(x, y, CELL_SIZE - margin * 2, CELL_SIZE - margin * 2)
            shadow_rect = rect.move(shadow_offset, shadow_offset)
            
            # 畫出陰影
            pygame.draw.rect(win, shadow_color, shadow_rect, border_radius=10)
            
            # 高亮方框或正常方框
            color = highlight_color if i * GRID_SIZE + j in highlight_cells else WHITE
            pygame.draw.rect(win, color, rect, border_radius=10)
            pygame.draw.rect(win, BLACK, rect, 3, border_radius=10)

# 顯示關卡信息
def display_level():
    display_message(f"Level: {level}", (WIDTH - 120, 10), TEXT_COLOR)

# 顯示文字訊息
def display_message(text, position, color=TEXT_COLOR):
    message = font.render(text, True, color)
    win.blit(message, position)

# 顯示正確序列的函數
def show_correct_sequence():
    for cell in sequence:
        display_grid([cell], highlight_color=ERROR_HIGHLIGHT)  # 使用紅色高亮顯示
        pygame.display.update()
        pygame.time.delay(500)
        display_grid()  # 清除高亮效果
        pygame.display.update()
        pygame.time.delay(300)

# 顯示排行榜
def display_leaderboard():
    win.fill(BLACK)
    display_message("排行榜", (WIDTH // 2 - 80, 50), WHITE)
    for i, entry in enumerate(leaderboard[:5]):
        text = f"{i + 1}. {entry['name']}: {entry['score']} 關"
        display_message(text, (WIDTH // 2 - 120, 100 + i * 40), WHITE)
    pygame.display.update()
    pygame.time.delay(3000)  # 顯示3秒後自動返回

# 玩家失敗時進行名字輸入的函數
def enter_player_name():
    global running
    name_input = ""
    input_active = True

    while input_active:
        win.fill(BLACK)
        display_message("Game over！Input your name：", (WIDTH // 2 - 150, HEIGHT // 3), WHITE)
        
        # 繪製輸入框的背景
        input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)
        pygame.draw.rect(win, WHITE, input_box)
        
        # 繪製輸入框的文字
        display_message(name_input, (WIDTH // 2 - 140, HEIGHT // 2 + 10), BLACK)  # 用黑色顯示輸入框內的文字
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                input_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    leaderboard.append({"name": name_input, "score": level})
                    leaderboard.sort(key=lambda x: x["score"], reverse=True)
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                else:
                    name_input += event.unicode  # 接收鍵盤輸入的字母並加到名字中
    game_over = True


# 遊戲主循環
while running:
    try:
        # 獲取影片的當前幀，將其作為背景
        frame = next(clip_frames)
        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        win.blit(pygame_frame, (0, 0))
    except StopIteration:
        # 若影片播放完畢，重置幀迭代
        clip_frames = clip.iter_frames(fps=240, dtype="uint8")
        frame = next(clip_frames)
        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        win.blit(pygame_frame, (0, 0))

    if not game_started:
        display_message(f"Level: {level}", (WIDTH - 120, 10), TEXT_COLOR)

        # 遊戲開始按鈕
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)
        shadow_rect = button_rect.move(5, 5)
        pygame.draw.rect(win, BUTTON_SHADOW_COLOR, shadow_rect, border_radius=20)
        pygame.draw.rect(win, BUTTON_COLOR, button_rect, border_radius=20)
        
        start_text = font.render("Game Start", True, TEXT_COLOR)
        text_rect = start_text.get_rect(center=button_rect.center)
        win.blit(start_text, text_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    game_started = True
                    sequence = generate_sequence(level)
                    showing_sequence = True
                    game_over = False
        
        pygame.display.update()
        continue
    if game_over: 
        # 如果遊戲結束，重置變量並返回主頁面 
        game_started = False 
        sequence = [] 
        player_sequence = [] 
        level = 1 
        continue

    # 顯示目前關卡
    display_level()
    
    
    # 顯示電腦的提示序列
    if showing_sequence:
        for cell in sequence:
            display_grid([cell])
            pygame.display.update()
            pygame.time.delay(500)
            win.blit(pygame_frame, (0, 0))  # 重新繪製影片幀
            display_grid()
            pygame.display.update()
            pygame.time.delay(300)
        showing_sequence = False
        player_turn = True
    
    # 如果是玩家回合，顯示 "換玩家" 提示
    if player_turn:
        display_message("change!", (WIDTH // 2 - 70, HEIGHT - 50))
    
    # 更新遊戲畫面
    display_grid()
    pygame.display.update()
    
    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
            x, y = event.pos
            row, col = (y - TOP_AREA_HEIGHT) // CELL_SIZE, x // CELL_SIZE
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                cell = row * GRID_SIZE + col
                player_sequence.append(cell)
                display_grid([cell])
                pygame.display.update()
                pygame.time.delay(200)
                
                if len(player_sequence) == len(sequence):
                    if player_sequence == sequence:
                        level += 1
                        sequence = generate_sequence(level)
                        player_sequence = []
                        showing_sequence = True
                        player_turn = False
                    else:
                        print("遊戲結束！你失敗了！")
                        show_correct_sequence()
                        enter_player_name()  # 呼叫名字輸入函數
                        display_leaderboard()  # 顯示排行榜
                        game_over = True