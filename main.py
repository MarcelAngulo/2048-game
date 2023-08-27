import pygame
import atexit
import random
import sys

NONE_TILE = 0

MAX_FPS = 60
GAME, GAMEOVER = 0, 1

FONT_FILE = "Anton-Regular.ttf"

def scaled_rect(real_w, real_h, rx1, ry1, rx2, ry2):
	return pygame.Rect(rx1*real_w, ry1*real_h, (rx2 - rx1)*real_w, (ry2 - ry1)*real_h)

class Board:

	def __init__(self, w=4, h=4, gn=1):
		self.w, self.h = w, h
		self.board = [[NONE_TILE for _ in range(self.w)] for _ in range(self.h)]
		self.movements = [[None for _ in range(self.w)] for _ in range(self.h)]
		self.generate_n = gn
		self.score = 0
		self.game_over = False

	def is_possible_move_up(self):
		for x in range(self.w):
			last_block_pos = -1
			last_block_t = 0
			for y in range(self.h):
				t = self.board[y][x]
				if t:
					if y - last_block_pos > 1 or t == last_block_t:
						return True
					else:
						last_block_pos = y
						last_block_t = t
		return False

	def is_possible_move_down(self):
		for x in range(self.w):
			last_block_pos = self.h
			last_block_t = 0
			for y in range(self.h-1, -1, -1):
				t = self.board[y][x]
				if t:
					if last_block_pos - y > 1 or t == last_block_t:
						return True
					else:
						last_block_pos = y
						last_block_t = t
		return False

	def is_possible_move_left(self):
		for y in range(self.h):
			last_block_pos = -1
			last_block_t = 0
			for x in range(self.w):
				t = self.board[y][x]
				if t:
					if x - last_block_pos > 1 or t == last_block_t:
						return True
					else:
						last_block_pos = x
						last_block_t = t
		return False

	def is_possible_move_right(self):
		for y in range(self.h):
			last_block_pos = self.w
			last_block_t = 0
			for x in range(self.w-1, -1, -1):
				t = self.board[y][x]
				if t:
					if last_block_pos - x > 1 or t == last_block_t:
						return True
					else:
						last_block_pos = x
						last_block_t = t
		return False

	def move_up(self):
		self.movements = [[None for _ in range(self.w)] for _ in range(self.h)]
		for x in range(self.w):
			locker = [False for _ in range(self.h)]
			t = self.board[0][x]
			if t:
				self.movements[0][x] = (0, 0, t)
			for y in range(1, self.h):
				t = self.board[y][x]
				if t:
					m = y
					t3 = t
					for dy in range(y-1, -1, -1):
						t2 = self.board[dy][x]
						if t2:
							if t != t2 or locker[dy]:
								break
							else:
								m = dy
								self.score += 2 ** t3
								t3 += 1
								locker[dy] = True
						else:
							m = dy
				
					self.board[y][x] = NONE_TILE
					self.board[m][x] = t3
					self.movements[y][x] = (m - y, 0, t)
				else:
					continue

	def move_down(self):
		self.movements = [[None for _ in range(self.w)] for _ in range(self.h)]
		for x in range(self.w):
			locker = [False for _ in range(self.h)]
			t = self.board[self.h-1][x]
			if t:
				self.movements[self.h-1][x] = (0, 0, t)
			for y in range(self.h-2, -1, -1):
				t = self.board[y][x]
				if t:
					m = y
					t3 = t
					for dy in range(y+1, self.h):
						t2 = self.board[dy][x]
						if t2:
							if t != t2 or locker[dy]:
								break
							else:
								m = dy
								self.score += 2 ** t3
								t3 += 1
								locker[dy] = True
						else:
							m = dy
				
					self.board[y][x] = NONE_TILE
					self.board[m][x] = t3
					self.movements[y][x] = (m - y, 0, t)
				else:
					continue

	def move_left(self):
		self.movements = [[None for _ in range(self.w)] for _ in range(self.h)]
		for y in range(self.h):
			locker = [False for _ in range(self.w)]
			t = self.board[y][0]
			if t:
				self.movements[y][0] = (0, 0, t)
			for x in range(1, self.w):
				t = self.board[y][x]
				if t:
					m = x
					t3 = t
					for dx in range(x-1, -1, -1):
						t2 = self.board[y][dx]
						if t2:
							if t != t2 or locker[dx]:
								break
							else:
								m = dx
								self.score += 2 ** t3
								t3 += 1
								locker[dx] = True
						else:
							m = dx
				
					self.board[y][x] = NONE_TILE
					self.board[y][m] = t3
					self.movements[y][x] = (0, m - x, t)
				else:
					continue

	def move_right(self):
		self.movements = [[None for _ in range(self.w)] for _ in range(self.h)]
		for y in range(self.h):
			locker = [False for _ in range(self.w)]
			t = self.board[y][self.w-1]
			if t:
				self.movements[y][self.w-1] = (0, 0, t)
			for x in range(self.w-2, -1, -1):
				t = self.board[y][x]
				if t:
					m = x
					t3 = t
					for dx in range(x+1, self.w):
						t2 = self.board[y][dx]
						if t2:
							if t != t2 or locker[dx]:
								break
							else:
								m = dx
								self.score += 2 ** t3
								t3 += 1
								locker[dx] = True
						else:
							m = dx
				
					self.board[y][x] = NONE_TILE
					self.board[y][m] = t3
					self.movements[y][x] = (0, m - x, t)
				else:
					continue


	def generate_block(self):
		# this function returns a Boolean value
		# if True is returned, it means game over
		# False means the opposite
		free = []
		counter = 0
		for x in range(self.w):
			for y in range(self.h):
				if not self.board[y][x]:
					free.append((x,y))
					counter += 1

		for i in range(self.generate_n):
			if counter == 0 and i < self.generate_n:
				self.game_over = True
				break
			x, y = free.pop(random.randint(0,counter-1))
			counter -= 1
			self.board[y][x] = random.randint(1,2)

	def check_gameover(self):
		return self.game_over or not (
			self.is_possible_move_up() or self.is_possible_move_down() or
			self.is_possible_move_left() or self.is_possible_move_right()
			)

class Game:

	PANEL_COLOR = 50, 50, 60
	BG_COLOR = 30, 20, 20
	BOARD_BG_COLOR = 50, 40, 40
	TILE_COLORS = (
		(35, 30, 30), # NONE
		(255, 209, 0), # 2
		(8, 208, 230), # 4
		(214, 27, 255), # 8
		(216, 22, 0), # 16
		(25, 190, 19), # 32
		(41, 20, 219), # 64
		(105, 24, 30), # 128
		(214, 91, 30), # 256
		(0, 0, 100), # 512
		(110, 100, 110), # 1024
		(10, 10, 5) # 2048
		)
	PANEL_FONT_COLOR = 255, 255, 255
	

	def __init__(self, scrn):
		self.scrn = scrn
		self.clock = pygame.time.Clock()
		self.animation_t_counter = pygame.time.get_ticks()
		self.total_animation_time = 50 # mili seconds
		self.updates_per_animation = 8
		self.update_animation_t_interval = self.total_animation_time / self.updates_per_animation
		self.in_animation = False

		self.board_w = 4
		self.board_h = 4
		self.generate_n = 1
		self.board = Board(self.board_w, self.board_h, self.generate_n)

	def start_loop(self, **kwargs):
		pygame.display.set_caption("2048")
		self.in_loop = True
		self.time_count = pygame.time.get_ticks()
		self.init_new_game()
		self.update_scales()

		while self.in_loop or self.in_animation:
			self.handle_events()
			self.update_state()
			self.render()
			self.clock.tick(MAX_FPS)
		else:
			return GAMEOVER, self.return_vals

	def init_new_game(self):
		self.board = Board(self.board_w, self.board_h, self.generate_n)
		self.board.generate_block()

	def handle_events(self):
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				exit(0)
			elif e.type == pygame.VIDEORESIZE:
				self.update_scales()

			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_q:
					exit(0)

				elif e.key == pygame.K_UP and not self.in_animation:
					if self.board.is_possible_move_up():
						self.board.move_up()
						self.board.generate_block()
						self.start_animation()

				elif e.key == pygame.K_DOWN and not self.in_animation:
					if self.board.is_possible_move_down():
						self.board.move_down()
						self.board.generate_block()
						self.start_animation()

				elif e.key == pygame.K_LEFT and not self.in_animation:
					if self.board.is_possible_move_left():
						self.board.move_left()
						self.board.generate_block()
						self.start_animation()

				elif e.key == pygame.K_RIGHT and not self.in_animation:
					if self.board.is_possible_move_right():
						self.board.move_right()
						self.board.generate_block()
						self.start_animation()

				elif e.key == pygame.K_r:
					self.init_new_game()

				self.update_score_points_sfc()
				self.update_score_pos()
				if self.board.check_gameover():
					self.in_loop = False
					self.return_vals = {'score': self.board.score}

	def start_animation(self):
		self.animation_t_counter = pygame.time.get_ticks()
		self.animation_frame_counter = 0
		self.in_animation = True

	def update_scales(self):
		scrn_w = self.scrn.get_width()
		scrn_h = self.scrn.get_height()
		panel_h_scale = 0.15 # 10% screen height
		self.panel_rect = scaled_rect(scrn_w, scrn_h, 0, 0, 1, panel_h_scale)
		self.bg_rect = scaled_rect(scrn_w, scrn_h, 0, panel_h_scale, 1, 1)

		tile_scale = 0.85 
		if self.bg_rect.h / self.board.h <= self.bg_rect.w / self.board.w:
			self.tile_sz = self.bg_rect.h * tile_scale / self.board.h
			self.pad = self.bg_rect.h * (1 - tile_scale) / (self.board.h + 1)
		else:
			self.tile_sz = self.bg_rect.w * tile_scale / self.board.w
			self.pad = self.bg_rect.w * (1 - tile_scale) / (self.board.w + 1)
		self.tile_sz = int(self.tile_sz)

		self.board_bg_rect = pygame.Rect(
			0, 0, self.tile_sz*self.board.w + self.pad*(self.board.w + 1), self.tile_sz*self.board.h + self.pad*(self.board.h + 1)
			)
		self.board_bg_rect.x =  (scrn_w - self.board_bg_rect.w)/2
		self.board_bg_rect.y = panel_h_scale*scrn_h + (self.bg_rect.h - self.board_bg_rect.h)/2

		self.font1 = pygame.font.Font(FONT_FILE, int(scrn_h * panel_h_scale * 0.74929))
		self.font2 = pygame.font.Font(FONT_FILE, int(self.tile_sz * 0.6 * 0.74929))
		
		self.score_label_sfc = self.font1.render("Score", True, self.PANEL_FONT_COLOR, self.PANEL_COLOR)
		self.update_score_points_sfc()
		self.update_score_pos()

		self.tile_sfcs = []
		for i in range(len(self.TILE_COLORS)):
			number = self.font2.render((f"{y}" if (y:=2**i) != 1 else ''), True, (255,255,255))
			sfc = pygame.Surface((self.tile_sz, self.tile_sz))
			sfc.fill(self.TILE_COLORS[i])
			pos = (sfc.get_width() - number.get_width())/2, (sfc.get_height() - number.get_height())/2
			sfc.blit(number, pos)
			self.tile_sfcs.append(sfc)

	def update_score_points_sfc(self):
		self.score_points_sfc = self.font1.render(f"{self.board.score}", True, self.PANEL_FONT_COLOR, self.PANEL_COLOR)

	def update_score_pos(self):
		scrn_w = self.scrn.get_width()
		scr_l_w = self.score_label_sfc.get_width()
		temp = (scrn_w - (scr_l_w  + scrn_w*0.05 + self.score_points_sfc.get_width()) )/2
		self.score_label_pos = temp, 0
		self.score_points_pos = temp + scr_l_w + scrn_w*0.05 , 0

	def update_state(self):
		if self.in_animation:
			if self.animation_frame_counter < self.updates_per_animation:
				if pygame.time.get_ticks() - self.animation_t_counter >= self.update_animation_t_interval:
					self.animation_frame_counter += 1
			else:
				self.in_animation = False

	def render(self):
		self.scrn.fill(self.PANEL_COLOR, self.panel_rect)
		self.scrn.blit(self.score_label_sfc, self.score_label_pos)
		self.scrn.blit(self.score_points_sfc, self.score_points_pos)
		self.scrn.fill(self.BG_COLOR, self.bg_rect)
		self.scrn.fill(self.BOARD_BG_COLOR, self.board_bg_rect)

		if self.in_animation:
			for x in range(self.board.w):
				for y in range(self.board.h):
					self.scrn.blit(self.tile_sfcs[0],
						(self.board_bg_rect.x + self.pad + (self.tile_sz + self.pad) * x,
						self.board_bg_rect.y + self.pad + (self.tile_sz + self.pad) * y)
					)
			for x in range(self.board.w):
				for y in range(self.board.h):
					block = self.board.movements[y][x]
					if block:
						dx = (self.tile_sz + self.pad) * block[1] // self.updates_per_animation * self.animation_frame_counter
						dy = (self.tile_sz + self.pad) * block[0] // self.updates_per_animation * self.animation_frame_counter
						self.scrn.blit(self.tile_sfcs[block[2]],
							(self.board_bg_rect.x + self.pad + (self.tile_sz + self.pad) * x + dx,
							self.board_bg_rect.y + self.pad + (self.tile_sz + self.pad) * y + dy)
							)
		else:
			for x in range(self.board.w):
				for y in range(self.board.h):
					self.scrn.blit(self.tile_sfcs[self.board.board[y][x]],
						(self.board_bg_rect.x + self.pad + (self.tile_sz + self.pad) * x,
						self.board_bg_rect.y + self.pad + (self.tile_sz + self.pad) * y)
					)

		pygame.display.flip()

	def pass_kwargs(self, **kwargs):
		pass

class GameOver:

	FONT_COLOR = 255, 255, 255
	BG_COLOR = 0, 0, 0

	def __init__(self, scrn):
		self.scrn = scrn
		self.clock = pygame.time.Clock()

		self.time_count = 0
		self.bip_interval = 800 # milliseconds
		self.visible = True
		self.final_score = 0

	def start_loop(self, **kwargs):
		self.update_scales()
		pygame.display.set_caption("Game Over")
		self.in_loop = True
		self.time_count = pygame.time.get_ticks()

		while self.in_loop:
			self.handle_events()
			self.update_state()
			self.render()
			self.clock.tick(MAX_FPS)
		else:
			return self.return_vals

	def handle_events(self):
		for ev in pygame.event.get():

			if ev.type == pygame.QUIT:
				exit(0)

			if ev.type == pygame.KEYDOWN:

				if ev.key == pygame.K_q:
					exit(0)
				else:
					self.in_loop = False
					self.return_vals = GAME, {}

			if ev.type == pygame.VIDEORESIZE:
				self.update_scales()

	def update_scales(self):
		scrn_w = self.scrn.get_width()
		scrn_h = self.scrn.get_height()
		ref = min(scrn_w, scrn_h)

		self.font1 = pygame.font.Font(FONT_FILE, ref // 6)
		self.font2 = pygame.font.Font(FONT_FILE, ref // 10)
		self.font3 = pygame.font.Font(FONT_FILE, ref // 9)


		self.game_over_label_sfc = self.font1.render(
			"Game Over!", True, self.FONT_COLOR, self.BG_COLOR)
		self.game_over_label_pos = scrn_w*0.5 - self.game_over_label_sfc.get_width()*0.5, scrn_h*0.05

		self.press_label_sfc = self.font2.render(
			"Press any key to continue", True, self.FONT_COLOR, self.BG_COLOR)
		self.press_label_pos = scrn_w*0.5 - self.press_label_sfc.get_width()*0.5, scrn_h - self.press_label_sfc.get_height()*1.5

		self.score_label_sfc = self.font3.render(
			"Score", True, self.FONT_COLOR, self.BG_COLOR)
		self.score_label_pos = (scrn_w - self.score_label_sfc.get_width())/2, scrn_h/2 - self.score_label_sfc.get_height()
		self.score_points_sfc = self.font3.render(
			f"{self.final_score}", True, self.FONT_COLOR, self.BG_COLOR)
		self.score_points_pos = (scrn_w - self.score_points_sfc.get_width())/2, scrn_h/2

	def update_state(self):
		if pygame.time.get_ticks() - self.time_count >= self.bip_interval:
			self.visible = not self.visible
			self.time_count = pygame.time.get_ticks()

	def render(self):
		self.scrn.fill(self.BG_COLOR)

		self.scrn.blit(
			self.game_over_label_sfc,
			self.game_over_label_pos
			)

		self.scrn.blit(
			self.score_label_sfc,
			self.score_label_pos
			)

		self.scrn.blit(
			self.score_points_sfc,
			self.score_points_pos
			)

		if self.visible:
			self.scrn.blit(
				self.press_label_sfc,
				self.press_label_pos
				)
		pygame.display.flip()

	def pass_kwargs(self, **kwargs):
		self.final_score = kwargs['score']

class Main:

	def __init__(self):
		pygame.init()
		atexit.register(pygame.quit)
		self.scrn = pygame.display.set_mode((600, 500), pygame.RESIZABLE)
		self.clock = pygame.time.Clock()
		self.loops = (
			Game(self.scrn),
			GameOver(self.scrn)
		)

	def run(self):
		self.current_loop = self.loops[GAME]
		while True:
			next_loop, kwargs = self.current_loop.start_loop()
			self.current_loop = self.loops[next_loop]
			self.current_loop.pass_kwargs(**kwargs)


if __name__ == '__main__':
	m = Main()
	if len(sys.argv) == 4:
		m.loops[GAME].board_h = int(sys.argv[1])
		m.loops[GAME].board_w = int(sys.argv[2])
		m.loops[GAME].generate_n = int(sys.argv[3])
	m.run()

'''
improve color pallette
'''