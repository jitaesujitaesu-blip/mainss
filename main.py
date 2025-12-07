######################################################################
""" AI를 해킹하라 - Pygame 게임 프로젝트 """
######################################################################

import pygame  # 게임 라이브러리
import sys  # 시스템 종료용
import os  # 파일 경로 관리
import math  # 수학 함수 (atan2, sqrt 등)
import random  # 랜덤 숫자 생성

class Game:
    """ 게임 메인 클래스 """
    
    # 색상 상수 정의 (R, G, B)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (150, 150, 150)
    HOVER_COLOR = (100, 100, 100)
    PLAYER_COLOR = (0, 200, 255)  # 플레이어 색상 (하늘색)
    ENEMY_TYPE1_COLOR = (255, 50, 50)  # 빨간색 - 근거리 적
    ENEMY_TYPE2_COLOR = (255, 150, 0)  # 주황색 - 원거리 적
    WARNING_COLOR = (255, 255, 0)  # 적 생성 예고 색상 (노란색)
    HP_BAR_BG = (100, 0, 0)  # 체력바 배경 (어두운 빨강)
    HP_BAR_FG = (0, 255, 0)  # 체력바 전경 (초록색)
    FLOOR_COLOR = (50, 50, 50)  # 바닥 색상 (어두운 회색)
    BULLET_COLOR = (255, 255, 255)  # 총알 색상 (흰색)
    
    # 게임 상수 정의
    PLAYER_SIZE = 40  # 플레이어 크기
    PLAYER_SPEED = 5  # 플레이어 이동 속도
    ENEMY_SIZE = 30  # 적 크기
    ENEMY_SPEED = 4  # 적 이동 속도
    ENEMY_TYPE2_DISTANCE = 200  # 2번 유형 적이 유지할 거리
    SAFE_RADIUS = 100  # 플레이어 주변 안전 반경 (적 생성 제외 영역)
    ENEMY_SPAWN_INTERVAL = 3000  # 적 생성 간격 (밀리초)
    WARNING_DURATION = 1500  # 적 생성 예고 지속 시간 (밀리초)
    ENEMY_DAMAGE = 15  # 적과 충돌 시 데미지
    ENEMY_BULLET_DAMAGE = 10  # 적 총알 데미지
    ENEMY_BULLET_SPEED = 3.33  # 적 총알 속도 (플레이어 속도의 2/3)
    BULLET_SIZE = 8  # 총알 크기
    ENEMY_TYPE1_HP = 10  # 근거리 적 체력
    ENEMY_TYPE2_HP = 5  # 원거리 적 체력
    
    def __init__(self):
        """ 게임 초기화 (생성자) """
        pygame.init()  # pygame 모듈 초기화
        
        # 현재 파일의 디렉토리를 작업 폴더로 변경 (이미지/폰트 파일 로드를 위함)
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # 전체화면 모드로 윈도우 생성
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()  # 화면 크기 저장
        pygame.display.set_caption("AI를 해킹하라")  # 윈도우 타이틀 설정
        
        # 폰트 설정 (한글 지원)
        try:
            # 폰트 파일 로드 시도
            self.title_font = pygame.font.Font("fonts/H2GPRM.TTF", 100)
            self.menu_font = pygame.font.Font("fonts/H2GPRM.TTF", 50)
            print("H2GPRM 폰트 로딩 성공")
        except Exception as e:
            # 폰트 로드 실패 시 시스템 폰트 사용
            print(f"폰트 로딩 실패: {e}, 시스템 폰트 사용")
            self.title_font = pygame.font.SysFont('malgungothic,nanumgothic,arial', 100)
            self.menu_font = pygame.font.SysFont('malgungothic,nanumgothic,arial', 50)
        
        # 게임 상태 변수 (화면 전환용)
        self.state = "menu"  # 현재 상태: menu, coding, tutorial, game, gameover
        self.clock = pygame.time.Clock()  # FPS 조절용 타이머 객체
        
        # 코딩 창 관련 변수
        self.code_input = ""  # 사용자가 입력한 코드
        self.code_error = False  # 에러 발생 여부
        self.code_error_timer = 0  # 에러 메시지 표시 시간
        self.available_points = 10  # 사용 가능한 간섭치 포인트
        self.error_message = ""  # 에러 메시지 내용
        self.cursor_position = 0  # 텍스트 입력 위치 (방향키로 이동 가능)
        self.cursor_visible = True  # 커서 표시 여부
        self.cursor_timer = 0  # 커서 깜빡임 타이머
        
        # 경험치 시스템 변수 (레벨업으로 증가)
        self.required_exp = 7  # 레벨업에 필요한 경험치
        self.level = 1  # 현재 레벨
        
        # 게임 타이머 변수 (레벨업 후에도 유지)
        self.game_start_time = 0  # 게임 시작 시간
        self.game_time = 0  # 경과 시간
        self.last_difficulty_increase_time = 0  # 마지막 난이도 증가 시간
        
        # 총 설정 변수 (코딩창에서 설정)
        self.gun_damage = 5  # 총알 데미지
        self.gun_attack_speed = 1  # 입력받은 공격속도 값
        self.gun_fire_interval = 1500  # 실제 발사 간격 (밀리초)
        self.gun_explosion_range = 50  # 폭발 범위 (반지름)
        self.last_shot_time = 0  # 마지막 발사 시간
        
        # 게임 플레이 변수 초기화 함수 호출
        self.init_game_variables()
        
        # 메뉴 버튼 좌표 설정 (Rect 객체 사용)
        button_width = 400
        button_height = 100
        button_spacing = 50
        start_y = self.height // 2
        
        # 시작 버튼 위치
        self.start_button = pygame.Rect(
            self.width // 2 - button_width // 2,
            start_y,
            button_width,
            button_height
        )
        
        # 게임설명 버튼 위치
        self.tutorial_button = pygame.Rect(
            self.width // 2 - button_width // 2,
            start_y + button_height + button_spacing,
            button_width,
            button_height
        )
        
        # 홈 버튼 위치 (게임오버 화면용)
        self.home_button = pygame.Rect(
            self.width // 2 - button_width // 2,
            self.height // 2 + 100,
            button_width,
            button_height
        )
    
    def init_game_variables(self):
        """게임 변수 초기화"""
        # 플레이 영역 설정 (화면 가장자리에서 50픽셀 여백)
        self.play_margin = 50
        self.play_area = pygame.Rect(
            self.play_margin,
            self.play_margin,
            self.width - 2 * self.play_margin,
            self.height - 2 * self.play_margin
        )
        
        # 플레이어 설정
        self.player_x = self.width // 2 - self.PLAYER_SIZE // 2
        self.player_y = self.height // 2 - self.PLAYER_SIZE // 2
        
        # 게임 타이머 (레벨업 후에도 유지)
        # game_start_time, game_time, last_difficulty_increase_time은 초기화하지 않음
        
        # 플레이어 체력
        self.player_hp = 100
        self.max_hp = 100
        
        # 적 시스템
        self.enemies = []
        self.enemy_warnings = []
        self.last_enemy_spawn = 0
        self.enemy_spawn_min = 1  # 최소 생성 수
        self.enemy_spawn_max = 3  # 최대 생성 수
        
        # 총알 시스템
        self.enemy_bullets = []  # 적 총알
        self.player_bullets = []  # 플레이어 총알
        self.explosions = []  # 폭발 이펙트
        
        # 경험치 시스템
        self.exp_items = []  # 경험치 아이템
        self.current_exp = 0  # 현재 경험치
        # required_exp와 level은 레벨업으로 증가하므로 초기화하지 않음
    
    def handle_menu_events(self):
        """메뉴 화면 이벤트 처리"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.collidepoint(mouse_pos):
                    self.state = "coding"  # 코딩 창으로 이동
                    self.code_input = ""  # 코드 입력 초기화
                    print("코딩 창 시작!")
                elif self.tutorial_button.collidepoint(mouse_pos):
                    self.state = "tutorial"
                    print("튜토리얼 시작!")
        
        return True
    
    def draw_button(self, button_rect, text, mouse_pos):
        """버튼 그리기"""
        color = self.HOVER_COLOR if button_rect.collidepoint(mouse_pos) else self.GRAY
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.WHITE, button_rect, 3, border_radius=10)
        
        text_surface = self.menu_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_menu(self):
        """메뉴 화면 그리기"""
        self.screen.fill(self.BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        # 제목
        title_text = self.title_font.render("AI를 해킹하라", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title_text, title_rect)
        
        # 버튼들
        self.draw_button(self.start_button, "시작", mouse_pos)
        self.draw_button(self.tutorial_button, "게임설명", mouse_pos)
        
        # ESC 안내
        info_text = self.menu_font.render("ESC: 종료", True, self.GRAY)
        info_rect = info_text.get_rect(center=(self.width // 2, self.height - 100))
        self.screen.blit(info_text, info_rect)
    
    def draw_tutorial(self):
        """튜토리얼 화면 그리기"""
        self.screen.fill(self.BLACK)
        
        title = self.title_font.render("튜토리얼", True, self.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)
        
        # 돌아가기 안내
        back_text = self.menu_font.render("ESC: 메뉴로 돌아가기", True, self.WHITE)
        back_rect = back_text.get_rect(center=(self.width // 2, self.height - 100))
        self.screen.blit(back_text, back_rect)
    
    def draw_gameover(self):
        """게임오버 화면 그리기"""
        self.screen.fill(self.BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        # "밴입니다." 텍스트
        ban_text = self.title_font.render("밴입니다.", True, (255, 0, 0))
        ban_rect = ban_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(ban_text, ban_rect)
        
        # 생존 시간 표시
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.menu_font.render(f"생존 시간: {minutes:02d}:{seconds:02d}", True, self.WHITE)
        time_rect = time_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(time_text, time_rect)
        
        # 홈 버튼
        self.draw_button(self.home_button, "홈으로", mouse_pos)
    
    def draw_coding(self):
        """코딩 창 그리기"""
        self.screen.fill((20, 20, 20))
        
        # 코딩 창 제목
        title = self.title_font.render("무기 코딩", True, (0, 255, 100))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # 설명
        instruction = self.menu_font.render("무기를 코딩하세요 (코드 입력 후 엔터)", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(self.width // 2, 200))
        self.screen.blit(instruction, instruction_rect)
        
        # 포인트 정보 박스 (오른쪽 위)
        point_box_width = 300
        point_box_height = 150
        point_box = pygame.Rect(self.width - point_box_width - 50, 50, point_box_width, point_box_height)
        pygame.draw.rect(self.screen, (40, 40, 40), point_box)
        pygame.draw.rect(self.screen, (0, 255, 100), point_box, 3)
        
        # 현재 입력된 값 계산 (실시간)
        current_total = 0
        try:
            # 현재 입력중인 텍스트에서 숫자 추출
            lines = [line.strip() for line in self.code_input.strip().split('\n')]
            for line in lines:
                if 'gun.gunsetting' in line and '(' in line:
                    # 닫는 괄호가 없어도 부분적으로 계산
                    start = line.index('(')
                    # 닫는 괄호가 있으면 그 위치까지, 없으면 끝까지
                    if ')' in line:
                        end = line.rindex(')')
                        params = line[start+1:end]
                    else:
                        params = line[start+1:]
                    
                    # 콤마로 분리
                    values = [v.strip() for v in params.split(',') if v.strip()]
                    # 숫자만 합산
                    for v in values:
                        try:
                            current_total += float(v)
                        except:
                            pass
        except:
            pass
        
        remaining_points = self.available_points - current_total
        
        # 포인트 텍스트 표시
        point_title = self.menu_font.render("간섭치", True, (200, 200, 200))
        
        # 간섭치 색상 및 텍스트 결정
        if remaining_points < 0:
            point_color = (255, 50, 50)  # 빨간색
            point_text = "초과"
        elif remaining_points == 0:
            point_color = (0, 0, 0)  # 검은색
            point_text = f"{remaining_points:.0f}"
        else:
            point_color = (0, 255, 100)  # 초록색
            point_text = f"{remaining_points:.0f}"
        
        point_value = self.menu_font.render(point_text, True, point_color)
        
        self.screen.blit(point_title, (point_box.centerx - point_title.get_width() // 2, point_box.top + 30))
        self.screen.blit(point_value, (point_box.centerx - point_value.get_width() // 2, point_box.top + 80))
        
        # 에러 메시지 표시 (코드 실행 시에만)
        if self.code_error or self.error_message:
            error_msg = self.error_message if self.error_message else "코드가 잘못되어 작동하지 않습니다."
            error_text = self.menu_font.render(error_msg, True, (255, 50, 50))
            error_rect = error_text.get_rect(center=(self.width // 2, 240))
            self.screen.blit(error_text, error_rect)
        
        # 코드 입력 창
        code_box = pygame.Rect(self.width // 2 - 500, 280, 1000, 500)
        pygame.draw.rect(self.screen, (0, 0, 0), code_box)
        pygame.draw.rect(self.screen, (0, 255, 100), code_box, 3)
        
        # 입력된 코드 표시 (여러 줄)
        y_offset = code_box.top + 20
        lines = self.code_input.split('\n')
        line_height = 55  # 줄 간격
        
        for line in lines[-15:]:  # 최대 15줄
            if line:
                code_text = self.menu_font.render(line[:60], True, (0, 255, 100))  # 최대 60자
            else:
                code_text = self.menu_font.render(" ", True, (0, 255, 100))
            self.screen.blit(code_text, (code_box.left + 20, y_offset))
            y_offset += line_height
        
        # 커서 깜빡임 처리
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer > 500:  # 0.5초마다 깜빡임
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # 커서 그리기
        if self.cursor_visible:
            # 커서 위치 계산
            text_before_cursor = self.code_input[:self.cursor_position]
            lines_before = text_before_cursor.split('\n')
            current_line_text = lines_before[-1] if lines_before else ""
            
            # 현재 줄의 텍스트 너비 계산
            text_width = self.menu_font.size(current_line_text[:60])[0] if current_line_text else 0
            text_height = self.menu_font.get_height()
            
            # 현재 줄 인덱스 (화면에 표시되는 줄 기준)
            current_line_index = len(lines_before) - 1
            display_line_index = min(current_line_index, 14)  # 최대 15줄만 표시
            
            # 커서 좌표
            cursor_x = code_box.left + 20 + text_width
            cursor_y = code_box.top + 20 + display_line_index * line_height
            
            # 커서 그리기 (세로 선)
            pygame.draw.line(self.screen, (0, 255, 100), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + text_height), 3)
        
        # 하단 안내
        esc_text = self.menu_font.render("ESC: 메뉴로 돌아가기", True, (150, 150, 150))
        self.screen.blit(esc_text, (self.width // 2 - 200, self.height - 80))
    
    def parse_gun_code(self, code):
        """총 코드 파싱"""
        try:
            # 코드를 줄 단위로 분리
            lines = [line.strip() for line in code.strip().split('\n')]
            
            # import gun 확인
            if not any('import gun' in line for line in lines):
                return False
            
            # gun.gunsetting 찾기
            for line in lines:
                if 'gun.gunsetting' in line or 'gun.gunsetting' in line.replace(' ', ''):
                    # 괄호 안의 내용 추출
                    if '(' in line and ')' in line:
                        start = line.index('(')
                        end = line.rindex(')')
                        params = line[start+1:end]
                        
                        # 콤마로 분리
                        values = [v.strip() for v in params.split(',')]
                        
                        if len(values) == 3:
                            # 모두 숫자인지 확인
                            damage = float(values[0])
                            attack_speed = float(values[1])
                            explosion_range = float(values[2])
                            
                            # 포인트 합계 검증
                            total_points = damage + attack_speed + explosion_range
                            if total_points > self.available_points:
                                self.error_message = "간섭치를 넘어 간섭할 수 없습니다."
                                return False
                            
                            # 유효성 검증
                            if damage > 0 and attack_speed > 0 and explosion_range >= 0:
                                self.gun_damage = damage
                                self.gun_attack_speed = attack_speed
                                # 공격속도 = 1.5 / 입력값 (초 단위를 밀리초로 변환)
                                self.gun_fire_interval = int((1.5 / attack_speed) * 1000)
                                # 기본 범위 15 + 입력값
                                self.gun_explosion_range = 15 + explosion_range
                                self.error_message = ""
                                return True
            
            return False
        except:
            return False
    
    def draw_game(self):
        """게임 화면 그리기"""
        self.screen.fill(self.BLACK)
        
        # 플레이 영역 (바닥) 그리기
        pygame.draw.rect(self.screen, (50, 50, 50), self.play_area)  # 어두운 회색 바닥
        pygame.draw.rect(self.screen, self.WHITE, self.play_area, 3)  # 흰색 테두리
        
        # 플레이어 그리기
        pygame.draw.rect(self.screen, self.PLAYER_COLOR, 
                        (self.player_x, self.player_y, self.PLAYER_SIZE, self.PLAYER_SIZE))
        
        # 적 생성 예고 표시
        current_time = pygame.time.get_ticks()
        if (current_time // 300) % 2 == 0:
            for warning in self.enemy_warnings:
                pygame.draw.rect(self.screen, self.WARNING_COLOR, 
                               (warning['x'], warning['y'], self.ENEMY_SIZE, self.ENEMY_SIZE), 3)
        
        # 적들 그리기
        for enemy in self.enemies:
            color = self.ENEMY_TYPE1_COLOR if enemy['type'] == 1 else self.ENEMY_TYPE2_COLOR
            enemy_x = enemy['x']
            enemy_y = enemy['y']
            
            pygame.draw.rect(self.screen, color, 
                           (enemy_x, enemy_y, self.ENEMY_SIZE, self.ENEMY_SIZE))
            
            # 적 체력바 표시 (체력이 최대가 아닐 때만)
            max_hp = self.ENEMY_TYPE1_HP if enemy['type'] == 1 else self.ENEMY_TYPE2_HP
            if enemy['hp'] < max_hp:
                hp_ratio = enemy['hp'] / max_hp
                hp_bar_current = int(self.ENEMY_SIZE * hp_ratio)
                hp_y = enemy_y - 8
                
                # 체력바 배경
                pygame.draw.rect(self.screen, (100, 0, 0),
                               (enemy_x, hp_y, self.ENEMY_SIZE, 4))
                # 현재 체력
                if hp_bar_current > 0:
                    pygame.draw.rect(self.screen, (0, 255, 0),
                                   (enemy_x, hp_y, hp_bar_current, 4))
        
        # 적 총알 그리기 (흰색)
        for bullet in self.enemy_bullets:
            pygame.draw.circle(self.screen, self.BULLET_COLOR, 
                             (int(bullet['x']), int(bullet['y'])), self.BULLET_SIZE)
        
        # 플레이어 총알 그리기 (노란색)
        for bullet in self.player_bullets:
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             (int(bullet['x']), int(bullet['y'])), self.BULLET_SIZE)
        
        # 폭발 이펙트 그리기 (반투명 원)
        current_time = pygame.time.get_ticks()
        for explosion in self.explosions[:]:
            # 폭발은 고정된 위치에 표시
            explosion_x = int(explosion['x'])
            explosion_y = int(explosion['y'])
            pygame.draw.circle(self.screen, (255, 100, 0), 
                             (explosion_x, explosion_y), 
                             int(self.gun_explosion_range), 2)
        
        # 경험치 아이템 그리기 (하늘색 원)
        for exp_item in self.exp_items:
            pygame.draw.circle(self.screen, (0, 200, 255), 
                             (int(exp_item['x']), int(exp_item['y'])), 8)
        
        # 타이머 표시 (좌측 상단)
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        timer_text = self.menu_font.render(f"{minutes:02d}:{seconds:02d}", True, self.WHITE)
        self.screen.blit(timer_text, (20, 20))
        
        # 경험치 바 표시 (상단 중앙)
        exp_bar_width = 400
        exp_bar_height = 20
        exp_bar_x = self.width // 2 - exp_bar_width // 2
        exp_bar_y = 20
        
        # 경험치 바 배경
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height))
        
        # 현재 경험치
        exp_ratio = min(self.current_exp / self.required_exp, 1.0)
        current_exp_width = int(exp_ratio * exp_bar_width)
        pygame.draw.rect(self.screen, (0, 200, 255), 
                        (exp_bar_x, exp_bar_y, current_exp_width, exp_bar_height))
        
        # 경험치 바 테두리
        pygame.draw.rect(self.screen, self.WHITE, 
                        (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height), 2)
        
        # 체력바 표시 (우측 상단)
        hp_bar_width = 300
        hp_bar_height = 30
        hp_bar_x = self.width - hp_bar_width - 20
        hp_bar_y = 20
        
        # 체력바 배경
        pygame.draw.rect(self.screen, self.HP_BAR_BG, 
                        (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        
        # 현재 체력
        current_hp_width = int((self.player_hp / self.max_hp) * hp_bar_width)
        pygame.draw.rect(self.screen, self.HP_BAR_FG, 
                        (hp_bar_x, hp_bar_y, current_hp_width, hp_bar_height))
        
        # 체력바 테두리
        pygame.draw.rect(self.screen, self.WHITE, 
                        (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
        
        # 체력 텍스트
        hp_text = self.menu_font.render(f"HP: {int(self.player_hp)}/{self.max_hp}", True, self.WHITE)
        hp_text_rect = hp_text.get_rect(center=(hp_bar_x + hp_bar_width // 2, hp_bar_y + hp_bar_height // 2))
        self.screen.blit(hp_text, hp_text_rect)
        
    def update_game(self):
        """게임 로직 업데이트"""
        # 타이머 업데이트
        current_time = pygame.time.get_ticks()
        self.game_time = (current_time - self.game_start_time) / 1000
        
        # 7초마다 난이도 증가 (생성 범위 +2)
        if self.game_time >= self.last_difficulty_increase_time + 7:
            self.enemy_spawn_min += 2
            self.enemy_spawn_max += 2
            self.last_difficulty_increase_time += 7
            print(f"난이도 증가! 적 생성 범위: {self.enemy_spawn_min}~{self.enemy_spawn_max}")
        
        # 적 생성 (3초마다)
        if current_time - self.last_enemy_spawn >= self.ENEMY_SPAWN_INTERVAL:
            # 현재 범위내에서 랜덤 생성
            spawn_count = random.randint(self.enemy_spawn_min, self.enemy_spawn_max)
            for _ in range(spawn_count):
                self.schedule_enemy_spawn()
            self.last_enemy_spawn = current_time
        
        # 예고된 적 생성 처리
        self.process_enemy_warnings(current_time)
        
        # 키 입력
        keys = pygame.key.get_pressed()
        
        # WASD 키로 이동
        if keys[pygame.K_w]:
            self.player_y -= self.PLAYER_SPEED
        if keys[pygame.K_s]:
            self.player_y += self.PLAYER_SPEED
        if keys[pygame.K_a]:
            self.player_x -= self.PLAYER_SPEED
        if keys[pygame.K_d]:
            self.player_x += self.PLAYER_SPEED
        
        # 맵 경계 체크
        if self.player_x < self.play_area.left:
            self.player_x = self.play_area.left
        if self.player_x + self.PLAYER_SIZE > self.play_area.right:
            self.player_x = self.play_area.right - self.PLAYER_SIZE
        if self.player_y < self.play_area.top:
            self.player_y = self.play_area.top
        if self.player_y + self.PLAYER_SIZE > self.play_area.bottom:
            self.player_y = self.play_area.bottom - self.PLAYER_SIZE
        
        # 자동 발사 (가까운 적 조준)
        if current_time - self.last_shot_time >= self.gun_fire_interval:
            if self.enemies:  # 적이 있을 때만 발사
                self.shoot_player_bullet()
                self.last_shot_time = current_time
        
        # 적 업데이트
        self.update_enemies(current_time)
        
        # 총알 업데이트
        self.update_enemy_bullets()
        self.update_player_bullets()
        
        # 경험치 아이템 획듍 체크
        player_rect = pygame.Rect(self.player_x, self.player_y, self.PLAYER_SIZE, self.PLAYER_SIZE)
        for exp_item in self.exp_items[:]:
            exp_rect = pygame.Rect(exp_item['x'] - 8, exp_item['y'] - 8, 16, 16)
            if player_rect.colliderect(exp_rect):
                self.current_exp += 1
                self.exp_items.remove(exp_item)
                
                # 레벨업 체크
                if self.current_exp >= self.required_exp:
                    self.level += 1
                    self.current_exp = 0
                    self.available_points += 3  # 간섭치 3 증가
                    
                    # 경험치 증가폭 계산: 레벨 3, 6, 9... 마다 +2씩 증가
                    if self.level % 3 == 0:
                        exp_increase = 3 + ((self.level // 3) * 2)
                    else:
                        exp_increase = 3 + (((self.level - 1) // 3) * 2)
                    
                    self.required_exp += exp_increase
                    print(f"레벨업! 레벨: {self.level}, 간섭치: {self.available_points}, 다음 레벨: {self.required_exp} (증가량: +{exp_increase})")
                    # 코딩 창으로 이동 (코드는 저장됨)
                    self.state = "coding"
                    self.error_message = ""  # 에러 메시지 초기화
                    return
        
        # 폭발 이펙트 업데이트 (0.2초 동안 범위 내 적들에게 피해)
        explosion_range_sq = self.gun_explosion_range * self.gun_explosion_range  # 제곱 미리 계산
        
        for explosion in self.explosions[:]:
            explosion_x = explosion['x']
            explosion_y = explosion['y']
            damaged_set = explosion['damaged_enemies']
            
            # 폭발 범위 내의 모든 적에게 피해
            for target_enemy in self.enemies[:]:
                enemy_id = id(target_enemy)
                
                # 이미 피해를 입은 적은 스킵
                if enemy_id in damaged_set:
                    continue
                
                # 적 사각형과 폭발 중심 사이의 최단 거리 계산 (적 전체를 히트박스로)
                enemy_left = target_enemy['x']
                enemy_right = target_enemy['x'] + self.ENEMY_SIZE
                enemy_top = target_enemy['y']
                enemy_bottom = target_enemy['y'] + self.ENEMY_SIZE
                
                # 폭발 중심에서 적 사각형까지 가장 가까운 점 찾기
                closest_x = max(enemy_left, min(explosion_x, enemy_right))
                closest_y = max(enemy_top, min(explosion_y, enemy_bottom))
                
                # 가장 가까운 점까지의 거리 제곱
                dx = closest_x - explosion_x
                dy = closest_y - explosion_y
                dist_sq = dx * dx + dy * dy
                
                # 범위 내에 있으면 피해
                if dist_sq <= explosion_range_sq:
                    target_enemy['hp'] -= self.gun_damage
                    damaged_set.add(enemy_id)
                    
                    if target_enemy['hp'] <= 0:
                        # 적이 죽었을 때 경험치 드롭 (1~2개)
                        enemy_center_x = target_enemy['x'] + self.ENEMY_SIZE // 2
                        enemy_center_y = target_enemy['y'] + self.ENEMY_SIZE // 2
                        drop_count = random.randint(1, 2)
                        for _ in range(drop_count):
                            # 적 위치에서 약간 흔어진 위치에 드롭
                            offset_x = random.randint(-15, 15)
                            offset_y = random.randint(-15, 15)
                            self.exp_items.append({
                                'x': enemy_center_x + offset_x,
                                'y': enemy_center_y + offset_y
                            })
                        self.enemies.remove(target_enemy)
            
            # 0.2초 후 폭발 제거
            if current_time - explosion['spawn_time'] >= 200:
                self.explosions.remove(explosion)
        
        # 충돌 체크
        self.check_collisions()
    
    def schedule_enemy_spawn(self):
        """적 생성 예고"""
        player_center_x = self.player_x + self.PLAYER_SIZE // 2
        player_center_y = self.player_y + self.PLAYER_SIZE // 2
        
        while True:
            enemy_x = random.randint(int(self.play_area.left), int(self.play_area.right - self.ENEMY_SIZE))
            enemy_y = random.randint(int(self.play_area.top), int(self.play_area.bottom - self.ENEMY_SIZE))
            
            dx = enemy_x - player_center_x
            dy = enemy_y - player_center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > self.SAFE_RADIUS:
                enemy_type = random.randint(1, 2)  # 1 또는 2번 유형
                self.enemy_warnings.append({
                    'x': enemy_x,
                    'y': enemy_y,
                    'type': enemy_type,
                    'spawn_time': pygame.time.get_ticks() + self.WARNING_DURATION
                })
                break
    
    def process_enemy_warnings(self, current_time):
        """예고 시간이 지난 적들을 실제로 생성"""
        warnings_to_remove = []
        
        for warning in self.enemy_warnings:
            if current_time >= warning['spawn_time']:
                # 실제 적 생성
                enemy_data = {
                    'x': warning['x'],
                    'y': warning['y'],
                    'type': warning['type'],
                    'hp': self.ENEMY_TYPE1_HP if warning['type'] == 1 else self.ENEMY_TYPE2_HP,
                    'last_shoot': current_time if warning['type'] == 2 else 0
                }
                
                # 2번 유형 적의 경우 랜덤 이동 방향 추가
                if warning['type'] == 2:
                    enemy_data['move_angle'] = random.uniform(0, 2 * math.pi)
                    enemy_data['move_timer'] = current_time
                
                self.enemies.append(enemy_data)
                warnings_to_remove.append(warning)
        
        # 생성된 예고 제거
        for warning in warnings_to_remove:
            self.enemy_warnings.remove(warning)
    
    def update_enemies(self, current_time):
        """적들을 플레이어 방향으로 이동"""
        for enemy in self.enemies:
            dx = self.player_x - enemy['x']
            dy = self.player_y - enemy['y']
            distance = math.sqrt(dx * dx + dy * dy)
            
            if enemy['type'] == 1:
                # 1번 유형: 플레이어를 직접 쫓아감
                if distance > 0:
                    enemy['x'] += (dx / distance) * self.ENEMY_SPEED
                    enemy['y'] += (dy / distance) * self.ENEMY_SPEED
            
            elif enemy['type'] == 2:
                # 2번 유형: 200 거리 유지하며 총알 발사
                if distance > self.ENEMY_TYPE2_DISTANCE:
                    # 너무 멀면 가까이
                    enemy['x'] += (dx / distance) * self.ENEMY_SPEED
                    enemy['y'] += (dy / distance) * self.ENEMY_SPEED
                elif distance < self.ENEMY_TYPE2_DISTANCE - 20:
                    # 너무 가까우면 랜덤 방향으로 이동
                    # 1초마다 새로운 방향 설정
                    if current_time - enemy['move_timer'] >= 1000:
                        enemy['move_angle'] = random.uniform(0, 2 * math.pi)
                        enemy['move_timer'] = current_time
                    
                    # 현재 설정된 방향으로 이동
                    enemy['x'] += math.cos(enemy['move_angle']) * self.ENEMY_SPEED
                    enemy['y'] += math.sin(enemy['move_angle']) * self.ENEMY_SPEED
                    
                    # 바닥 밖으로 나가지 않도록 제한
                    enemy['x'] = max(self.play_area.left, min(enemy['x'], self.play_area.right - self.ENEMY_SIZE))
                    enemy['y'] = max(self.play_area.top, min(enemy['y'], self.play_area.bottom - self.ENEMY_SIZE))
                
                # 1초마다 총알 발사
                if current_time - enemy['last_shoot'] >= 1000:
                    self.shoot_enemy_bullet(enemy['x'], enemy['y'])
                    enemy['last_shoot'] = current_time
    
    def shoot_enemy_bullet(self, enemy_x, enemy_y):
        """적이 플레이어 주변 랜덤 위치를 향해 총알 발사"""
        # 플레이어 중심 좌표
        player_center_x = self.player_x + self.PLAYER_SIZE // 2
        player_center_y = self.player_y + self.PLAYER_SIZE // 2
        
        # 플레이어 주변 반지름 35 내의 랜덤 위치
        angle = random.uniform(0, 2 * math.pi)
        random_radius = random.uniform(0, 35)
        target_x = player_center_x + random_radius * math.cos(angle)
        target_y = player_center_y + random_radius * math.sin(angle)
        
        # 총알 발사 방향 계산
        dx = target_x - enemy_x
        dy = target_y - enemy_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.enemy_bullets.append({
                'x': enemy_x + self.ENEMY_SIZE // 2,
                'y': enemy_y + self.ENEMY_SIZE // 2,
                'vx': (dx / distance) * self.ENEMY_BULLET_SPEED,
                'vy': (dy / distance) * self.ENEMY_BULLET_SPEED
            })
    
    def shoot_player_bullet(self):
        """플레이어가 가장 가까운 적을 자동 조준하여 총알 발사"""
        if not self.enemies:
            return
        
        player_center_x = self.player_x + self.PLAYER_SIZE // 2
        player_center_y = self.player_y + self.PLAYER_SIZE // 2
        
        # 가장 가까운 적 찾기 (거리와 방향을 한 번에 계산)
        closest_dx = None
        closest_dy = None
        min_distance = float('inf')
        
        for enemy in self.enemies:
            enemy_center_x = enemy['x'] + self.ENEMY_SIZE // 2
            enemy_center_y = enemy['y'] + self.ENEMY_SIZE // 2
            dx = enemy_center_x - player_center_x
            dy = enemy_center_y - player_center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < min_distance:
                min_distance = distance
                closest_dx = dx
                closest_dy = dy
        
        if closest_dx is not None and min_distance > 0:
            # 이미 계산된 방향을 사용하여 발사
            bullet_speed = 10
            self.player_bullets.append({
                'x': player_center_x,
                'y': player_center_y,
                'vx': (closest_dx / min_distance) * bullet_speed,
                'vy': (closest_dy / min_distance) * bullet_speed
            })
    
    def update_enemy_bullets(self):
        """적 총알 이동"""
        # 역순회로 제거하면서 이동
        for i in range(len(self.enemy_bullets) - 1, -1, -1):
            bullet = self.enemy_bullets[i]
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            
            # 화면 밖으로 나가면 제거
            if (bullet['x'] < 0 or bullet['x'] > self.width or
                bullet['y'] < 0 or bullet['y'] > self.height):
                self.enemy_bullets.pop(i)
    
    def update_player_bullets(self):
        """플레이어 총알 이동"""
        # 역순회로 제거하면서 이동
        for i in range(len(self.player_bullets) - 1, -1, -1):
            bullet = self.player_bullets[i]
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            
            # 화면 밖으로 나가면 제거
            if (bullet['x'] < 0 or bullet['x'] > self.width or
                bullet['y'] < 0 or bullet['y'] > self.height):
                self.player_bullets.pop(i)
    
    def check_collisions(self):
        """충돌 체크"""
        player_rect = pygame.Rect(self.player_x, self.player_y, self.PLAYER_SIZE, self.PLAYER_SIZE)
        
        # 플레이어와 적 충돌
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], self.ENEMY_SIZE, self.ENEMY_SIZE)
            
            if player_rect.colliderect(enemy_rect):
                self.player_hp -= self.ENEMY_DAMAGE
                self.enemies.pop(i)
                
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.state = "gameover"
                    return
        
        # 플레이어와 적 총알 충돌
        for bullet in self.enemy_bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'] - self.BULLET_SIZE, bullet['y'] - self.BULLET_SIZE,
                                     self.BULLET_SIZE * 2, self.BULLET_SIZE * 2)
            
            if player_rect.colliderect(bullet_rect):
                self.player_hp -= self.ENEMY_BULLET_DAMAGE
                self.enemy_bullets.remove(bullet)
                
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.state = "gameover"
                    return
        
        # 플레이어 총알과 적 충돌 (폭발 시스템)
        current_time = pygame.time.get_ticks()
        bullet_size_2 = self.BULLET_SIZE * 2
        
        for bullet in self.player_bullets[:]:
            bx = bullet['x']
            by = bullet['y']
            bullet_rect = pygame.Rect(bx - self.BULLET_SIZE, by - self.BULLET_SIZE,
                                     bullet_size_2, bullet_size_2)
            
            for enemy in self.enemies:
                enemy_rect = pygame.Rect(enemy['x'], enemy['y'], self.ENEMY_SIZE, self.ENEMY_SIZE)
                
                if bullet_rect.colliderect(enemy_rect):
                    # 폭발 생성
                    self.explosions.append({
                        'x': bx,
                        'y': by,
                        'spawn_time': current_time,
                        'damaged_enemies': set()
                    })
                    
                    self.player_bullets.remove(bullet)
                    break
    
    def handle_game_events(self):
        """게임 화면 이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
        
        return True
    
    def handle_game_tutorial_events(self):
        """게임/튜토리얼 화면 이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
        
        return True
    
    def handle_gameover_events(self):
        """게임오버 화면 이벤트 처리"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.home_button.collidepoint(mouse_pos):
                    self.state = "menu"
        
        return True
    
    def handle_coding_events(self):
        """코딩 창 이벤트 처리"""
        # 에러 메시지 타이머 처리
        if self.code_error:
            current_time = pygame.time.get_ticks()
            if current_time - self.code_error_timer > 2000:  # 2초 후 에러 메시지 숨김
                self.code_error = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Shift + Enter: 줄바꿈
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.code_input = self.code_input[:self.cursor_position] + '\n' + self.code_input[self.cursor_position:]
                        self.cursor_position += 1
                        self.code_error = False
                    # Enter만: 코드 파싱 시도
                    elif self.code_input.strip():
                        if self.parse_gun_code(self.code_input):
                            # 코드가 올바르면 게임 재개 (코드는 저장됨)
                            self.state = "game"
                            # 첫 시작일 때만 게임 변수와 타이머 초기화
                            if self.game_start_time == 0:
                                self.init_game_variables()
                                self.game_start_time = pygame.time.get_ticks()
                                self.last_difficulty_increase_time = 0
                            print(f"입력된 코드: {self.code_input}")
                            print(f"총 설정 - 데미지: {self.gun_damage}, 공격속도: {self.gun_attack_speed} (발사간격: {self.gun_fire_interval}ms), 폭발범위: {self.gun_explosion_range}")
                        else:
                            # 코드가 잘못되었으면 에러 표시 및 코드 초기화
                            self.code_error = True
                            self.code_error_timer = pygame.time.get_ticks()
                            self.code_input = ""
                            self.cursor_position = 0
                            print("코드 에러!")
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor_position > 0:
                        self.code_input = self.code_input[:self.cursor_position-1] + self.code_input[self.cursor_position:]
                        self.cursor_position -= 1
                    self.code_error = False  # 입력 시작하면 에러 메시지 숨김
                elif event.key == pygame.K_DELETE:
                    if self.cursor_position < len(self.code_input):
                        self.code_input = self.code_input[:self.cursor_position] + self.code_input[self.cursor_position+1:]
                elif event.key == pygame.K_LEFT:
                    if self.cursor_position > 0:
                        self.cursor_position -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.cursor_position < len(self.code_input):
                        self.cursor_position += 1
                elif event.key == pygame.K_HOME:
                    self.cursor_position = 0
                elif event.key == pygame.K_END:
                    self.cursor_position = len(self.code_input)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                else:
                    # 일반 문자 입력
                    if len(self.code_input) < 200:  # 최대 길이 제한
                        self.code_input = self.code_input[:self.cursor_position] + event.unicode + self.code_input[self.cursor_position:]
                        self.cursor_position += len(event.unicode)
                        self.code_error = False  # 입력 시작하면 에러 메시지 숨김
        
        return True
    
    def run(self):
        """메인 게임 루프"""
        running = True
        
        while running:
            if self.state == "menu":
                running = self.handle_menu_events()
                self.draw_menu()
            
            elif self.state == "coding":
                running = self.handle_coding_events()
                self.draw_coding()
            
            elif self.state == "tutorial":
                running = self.handle_game_tutorial_events()
                self.draw_tutorial()
            
            elif self.state == "game":
                running = self.handle_game_events()
                self.update_game()
                self.draw_game()
            
            elif self.state == "gameover":
                running = self.handle_gameover_events()
                self.draw_gameover()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
