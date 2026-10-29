import pygame
import random
import sys

# 초기화
pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("축구 심판 시뮬레이터 - Football Referee Simulator")
clock = pygame.time.Clock()

# 색상 정의
GREEN = (46, 139, 87)
DARK_GREEN = (34, 102, 64)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
RED = (220, 50, 50)
YELLOW = (240, 200, 50)
BLUE = (50, 120, 220)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# 폰트 설정 (시스템 기본 폰트 사용)
try:
    font_large = pygame.font.SysFont("malgungothic", 36, bold=True)
    font_medium = pygame.font.SysFont("malgungothic", 24)
    font_small = pygame.font.SysFont("malgungothic", 18)
except:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

class GameState:
    MENU = 1
    MATCH = 2
    INCIDENT = 3
    VAR = 4
    POST_MATCH = 5
    UPGRADE = 6

class RefereeSimulator:
    def __init__(self):
        self.state = GameState.MENU
        self.ref_name = "김심판"
        self.league = "지역 아마추어 리그 (Division 5)"
        self.reputation = 50
        self.money = 100000
        
        # 능력치
        self.stamina = 50
        self.authority = 50
        self.vision = 50
        
        # 경기 관련 변수
        self.match_time = 0
        self.composure = 100
        self.correct_count = 0
        self.total_incidents = 3
        self.current_incident_idx = 0
        self.current_event = None
        self.match_report_data = {}
        
        # 필드 위 선수/심판 위치 시뮬레이션용
        self.ref_pos = [WIDTH // 2, HEIGHT // 2]
        self.ball_pos = [WIDTH // 2, HEIGHT // 2]

    def reset_match(self):
        self.match_time = 0
        self.composure = 100
        self.correct_count = 0
        self.current_incident_idx = 0
        self.events_list = self.generate_events()

    def generate_events(self):
        event_pool = [
            {"type": "FOUL", "desc": "미드필드 지역에서 거친 태클 발생!", "correct": ["1", "2", "3"]},
            {"type": "OFFSIDE", "desc": "공격 팀의 침투, 오프사이드 의심!", "correct": ["1"]},
            {"type": "PENALTY", "desc": "페널티 박스 안에서 수비수와 충돌!", "correct": ["3", "4"]},
            {"type": "DIVE", "desc": "발이 걸리지 않았는데 넘어졌습니다 (할리우드 의심)", "correct": ["2"]}
        ]
        return random.sample(event_pool, self.total_incidents)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                self.handle_click(pos)

    def handle_click(self, pos):
        x, y = pos
        if self.state == GameState.MENU:
            if 362 <= x <= 662:
                if 300 <= y <= 350: # 경기 시작
                    self.reset_match()
                    self.state = GameState.MATCH
                elif 380 <= y <= 430: # 정보 확인
                    pass
                elif 460 <= y <= 510: # 상점
                    self.state = GameState.UPGRADE
                elif 540 <= y <= 590: # 종료
                    pygame.quit()
                    sys.exit()

        elif self.state == GameState.INCIDENT:
            # 판정 선택 버튼 (1: 진행, 2: 구두경고, 3: 경고, 4: 퇴장)
            choice = None
            if 200 <= y <= 260: choice = "1"
            elif 280 <= y <= 340: choice = "2"
            elif 360 <= y <= 420: choice = "3"
            elif 440 <= y <= 500: choice = "4"

            if choice:
                self.process_judgment(choice)

        elif self.state == GameState.VAR:
            # VAR 선택 (1: 번복, 2: 유지)
            if 360 <= y <= 420:
                if 250 <= x <= 480: # 번복
                    self.resolve_var(True)
                elif 544 <= x <= 774: # 유지
                    self.resolve_var(False)

        elif self.state == GameState.POST_MATCH:
            if 362 <= x <= 662 and 600 <= y <= 650:
                self.state = GameState.MENU

        elif self.state == GameState.UPGRADE:
            if 100 <= x <= 300 and 600 <= y <= 650: # 돌아가기
                self.state = GameState.MENU
            elif 350 <= x <= 674:
                if 250 <= y <= 310 and self.money >= 30000:
                    self.money -= 30000
                    self.vision += 10
                elif 340 <= y <= 400 and self.money >= 30000:
                    self.money -= 30000
                    self.stamina += 10
                elif 430 <= y <= 490 and self.money >= 30000:
                    self.money -= 30000
                    self.authority += 10

    def process_judgment(self, choice):
        event = self.current_event
        is_correct = choice in event["correct"]
        
        # 시야 스탯 보정
        if not is_correct and random.random() < (self.vision * 0.002):
            is_correct = True # 시야가 좋으면 오심을 정심으로 보정

        if is_correct:
            self.correct_count += 1
            self.composure = min(100, self.composure + 5)
            self.match_result_msg = "✨ 정확한 판정입니다! 경기가 원활히 진행됩니다."
        else:
            self.composure -= 30
            self.reputation -= 5
            self.match_result_msg = "❌ 판정 논란 발생! 선수들이 거세게 항의합니다!"
            
            # 치명적 오심 시 VAR 확률 발동
            if event["type"] in ["PENALTY", "OFFSIDE"] and random.random() > 0.3:
                self.state = GameState.VAR
                return

        self.next_incident_flow()

    def resolve_var(self, overturn):
        if overturn:
            self.correct_count += 1
            self.composure += 10
            self.match_result_msg = "🔄 VAR 판독 결과: 판정이 올바르게 번복되었습니다."
        else:
            self.match_result_msg = "🔒 VAR 판독 결과: 원심이 유지되었습니다. 경기장이 야유로 가득 찹니다!"
        
        self.next_incident_flow()

    def next_incident_flow(self):
        self.current_incident_idx += 1
        if self.current_incident_idx >= self.total_incidents or self.composure <= 0:
            self.finish_match()
        else:
            self.state = GameState.MATCH

    def finish_match(self):
        accuracy = (self.correct_count / self.total_incidents) * 100
        earned = 50000 + (self.correct_count * 15000)
        self.money += earned
        
        if accuracy >= 70:
            self.reputation += 10
            eval_text = "냉정하고 침착한 판정으로 호평을 받았습니다."
        else:
            self.reputation -= 15
            eval_text = "오심 논란으로 협회와 언론의 뭇매를 맞았습니다."

        # 승급 체크
        if self.reputation >= 80 and "Division 5" in self.league:
            self.league = "프로 2부 리그 (Division 2)"
            eval_text += "\n🎉 축하합니다! 상위 리그로 승격되었습니다!"
        elif self.reputation >= 130 and "Division 2" in self.league:
            self.league = "프리미어리그 (Premier League)"
            eval_text += "\n🏆 최고 무대인 프리미어리그로 승격되었습니다!"

        self.match_report_data = {
            "accuracy": accuracy,
            "correct": self.correct_count,
            "total": self.total_incidents,
            "earned": earned,
            "eval": eval_text
        }
        self.state = GameState.POST_MATCH

    def update(self):
        if self.state == GameState.MATCH:
            self.match_time += 1
            # 경기 중 랜덤하게 돌발 상황 발생
            if self.match_time % 120 == 0:
                self.current_event = self.events_list[self.current_incident_idx]
                self.state = GameState.INCIDENT

    def render(self):
        screen.fill(GREEN)

        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.MATCH:
            self.render_pitch()
        elif self.state == GameState.INCIDENT:
            self.render_pitch()
            self.render_incident_modal()
        elif self.state == GameState.VAR:
            self.render_pitch()
            self.render_var_modal()
        elif self.state == GameState.POST_MATCH:
            self.render_post_match()
        elif self.state == GameState.UPGRADE:
            self.render_upgrade()

        pygame.display.flip()

    def render_menu(self):
        title = font_large.render("축구 심판 시뮬레이터", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        sub = font_medium.render(f"심판: {self.ref_name} | 소속: {self.league}", True, WHITE)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 220))

        buttons = [
            ("경기 배정받기", 300),
            ("심판 정보", 380),
            ("훈련 및 상점", 460),
            ("게임 종료", 540)
        ]

        for text, y in buttons:
            pygame.draw.rect(screen, DARK_GREEN, (362, y, 300, 50), border_radius=8)
            pygame.draw.rect(screen, WHITE, (362, y, 300, 50), 2, border_radius=8)
            txt = font_medium.render(text, True, WHITE)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y + 12))

    def render_pitch(self):
        # 축구장 그래픽 (탑뷰)
        pygame.draw.rect(screen, DARK_GREEN, (50, 50, WIDTH - 100, HEIGHT - 100), border_radius=15)
        # 하프라인 및 센터서클
        pygame.draw.line(screen, WHITE, (WIDTH // 2, 50), (WIDTH // 2, HEIGHT - 50), 3)
        pygame.draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT // 2), 70, 3)
        # 페널티박스
        pygame.draw.rect(screen, WHITE, (50, HEIGHT // 2 - 150, 150, 300), 3)
        pygame.draw.rect(screen, WIDTH - 200, HEIGHT // 2 - 150, 150, 300, 3)

        # 선수 및 심판 원 표시
        pygame.draw.circle(screen, BLUE, (WIDTH // 3, HEIGHT // 2 - 50), 12)
        pygame.draw.circle(screen, RED, (WIDTH // 3 + 50, HEIGHT // 2 + 50), 12)
        pygame.draw.circle(screen, YELLOW, (WIDTH // 2, HEIGHT // 2), 10) # 심판

        # 상단 HUD
        hud_bg = pygame.Rect(50, 20, WIDTH - 100, 50)
        pygame.draw.rect(screen, BLACK, hud_bg, border_radius=8)
        
        info_txt = font_medium.render(f"리그: {self.league} | 평판: {self.reputation} | 자금: {self.money:,}원", True, WHITE)
        screen.blit(info_txt, (70, 32))
        
        comp_txt = font_medium.render(f"멘탈: {self.composure}%", True, YELLOW if self.composure > 40 else RED)
        screen.blit(comp_txt, (WIDTH - 250, 32))

    def render_incident_modal(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(200, 120, WIDTH - 400, 520)
        pygame.draw.rect(screen, BLACK, box, border_radius=12)
        pygame.draw.rect(screen, WHITE, box, 3, border_radius=12)

        title = font_large.render("🚨 돌발 상황 발생!", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        desc = font_medium.render(self.current_event["desc"], True, WHITE)
        screen.blit(desc, (WIDTH // 2 - desc.get_width() // 2, 210))

        options = [
            ("1. 경기 진행 (Play On / Advantage)", 280),
            ("2. 구두 경고 (Warning)", 360),
            ("3. 경고 (Yellow Card)", 440),
            ("4. 퇴장 (Red Card)", 520)
        ]

        for text, y in options:
            pygame.draw.rect(screen, DARK_GRAY, (250, y, WIDTH - 500, 50), border_radius=6)
            txt = font_medium.render(text, True, WHITE)
            screen.blit(txt, (270, y + 12))

    def render_var_modal(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(200, 180, WIDTH - 400, 360)
        pygame.draw.rect(screen, BLACK, box, border_radius=12)
        pygame.draw.rect(screen, WHITE, box, 3, border_radius=12)

        title = font_large.render("📺 VAR(비디오 판독) 리뷰 권고", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 210))

        desc = font_medium.render("리플레이를 확인했습니다. 판정을 어떻게 하시겠습니까?", True, WHITE)
        screen.blit(desc, (WIDTH // 2 - desc.get_width() // 2, 280))

        # 버튼
        pygame.draw.rect(screen, BLUE, (250, 380, 230, 60), border_radius=8)
        t1 = font_medium.render("판정 번복", True, WHITE)
        screen.blit(t1, (310, 395))

        pygame.draw.rect(screen, RED, (544, 380, 230, 60), border_radius=8)
        t2 = font_medium.render("원심 유지", True, WHITE)
        screen.blit(t2, (604, 395))

    def render_post_match(self):
        box = pygame.Rect(200, 100, WIDTH - 400, 580)
        pygame.draw.rect(screen, BLACK, box, border_radius=12)
        pygame.draw.rect(screen, WHITE, box, 3, border_radius=12)

        title = font_large.render("📊 경기 종료 리포트", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 130))

        d = self.match_report_data
        lines = [
            f"판정 정확도: {d['accuracy']:.1f}% ({d['correct']}/{d['total']})",
            f"경기 수당 획득: +{d['earned']:,}원",
            f"\n[평가 및 피드백]",
            f"{d['eval']}"
        ]

        y_offset = 210
        for line in lines:
            txt = font_medium.render(line, True, YELLOW if "🎉" in line or "🏆" in line else WHITE)
            screen.blit(txt, (240, y_offset))
            y_offset += 40

        # 확인 버튼
        pygame.draw.rect(screen, DARK_GREEN, (362, 600, 300, 50), border_radius=8)
        pygame.draw.rect(screen, WHITE, (362, 600, 300, 50), 2, border_radius=8)
        bt_txt = font_medium.render("메인으로 돌아가기", True, WHITE)
        screen.blit(bt_txt, (WIDTH // 2 - bt_txt.get_width() // 2, 612))

    def render_upgrade(self):
        title = font_large.render("📈 심판 트레이닝 센터", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        info = font_medium.render(f"보유 자금: {self.money:,}원", True, YELLOW)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 140))

        stats = [
            (f"1. 시야 훈련 (현재: {self.vision}) - 비용: 30,000원", 250),
            (f"2. 체력 훈련 (현재: {self.stamina}) - 비용: 30,000원", 340),
            (f.format(), 430) if False else (f"3. 권위/카리스마 스터디 (현재: {self.authority}) - 비용: 30,000원", 430)
        ]

        for text, y in stats:
            pygame.draw.rect(screen, DARK_GREEN, (250, y, WIDTH - 500, 50), border_radius=6)
            pygame.draw.rect(screen, WHITE, (250, y, WIDTH - 500, 50), 2, border_radius=6)
            txt = font_small.render(text, True, WHITE)
            screen.blit(txt, (270, y + 16))

        # 돌아가기 버튼
        pygame.draw.rect(screen, DARK_GRAY, (100, 600, 200, 50), border_radius=6)
        back_txt = font_medium.render("돌아가기", True, WHITE)
        screen.blit(back_txt, (160, 612))

if __name__ == "__main__":
    game = RefereeSimulator()
    game.run()
