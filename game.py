from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GLUT as _glut_mod
from OpenGL.GLUT import *
GLUT_BITMAP_HELVETICA_18 = getattr(_glut_mod, 'GLUT_BITMAP_HELVETICA_18', None) or getattr(_glut_mod, 'GLUT_BITMAP_HELVETICA_12', None)
import math, random, time, sys, signal

WINDOW_WIDTH, WINDOW_HEIGHT, FPS = 1024, 768, 60
BLACK, WHITE, GREEN, RED, BLUE, CYAN, YELLOW, ORANGE, GRAY, DARK_GRAY, PURPLE = (0,0,0), (1,1,1), (0,1,0), (1,0,0), (0,0,1), (0,1,1), (1,1,0), (1,0.5,0), (0.4,0.4,0.4), (0.2,0.2,0.2), (1,0,1)

class Vector3: 
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    def copy(self):
        return Vector3(self.x, self.y, self.z)
    
class Player:
    def __init__(self):
        self.position = Vector3(-8, 0.5, -8)
        self.size, self.speed = 0.5, 0.1
        self.rotation = 0  
        self.velocity_y = 0  
        self.on_ground = True  
        self.gravity = -0.008  
        self.jump_strength = 0.35  
        
    def update(self, keys, walls):
        old_pos = self.position.copy()
        if keys.get(b'a', False) or keys.get(b'A', False):
            self.rotation = (self.rotation + 5) % 360 
        if keys.get(b'd', False) or keys.get(b'D', False):
            self.rotation = (self.rotation - 5) % 360  
        if keys.get(b'w', False) or keys.get(b'W', False):
            move = self.speed
            delta_x = math.sin(math.radians(self.rotation)) * move
            delta_z = math.cos(math.radians(self.rotation)) * move
            self.position.x += delta_x
            self.position.z += delta_z
            
        if keys.get(b's', False) or keys.get(b'S', False):
            move = self.speed
            delta_x = math.sin(math.radians(self.rotation)) * move
            delta_z = math.cos(math.radians(self.rotation)) * move
            self.position.x -= delta_x
            self.position.z -= delta_z
        
        if keys.get('up', False):
            self.position.z -= self.speed  
        if keys.get('down', False):
            self.position.z += self.speed 
        if keys.get('left', False):
            self.position.x -= self.speed  
        if keys.get('right', False):
            self.position.x += self.speed  
        
        if keys.get(b' ', False) and self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False
            
            jump_forward_speed = 0.05 
            delta_x = math.sin(math.radians(self.rotation)) * jump_forward_speed
            delta_z = math.cos(math.radians(self.rotation)) * jump_forward_speed
            self.position.x += delta_x
            self.position.z += delta_z
        
        if not self.on_ground:
            self.velocity_y += self.gravity
            self.position.y += self.velocity_y
            if self.position.y <= 0.5:
                self.position.y = 0.5
                self.velocity_y = 0
                self.on_ground = True
        if self.check_wall_collision(walls):
            self.position.x = old_pos.x
            self.position.z = old_pos.z
        
        self.position.x = max(-9.5, min(9.5, self.position.x))
        self.position.z = max(-9.5, min(9.5, self.position.z))
    
    def check_wall_collision(self, walls):
        return any(abs(self.position.x - w.position.x) < w.size.x/2 + self.size and
                  abs(self.position.z - w.position.z) < w.size.z/2 + self.size for w in walls)
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation, 0, 1, 0)  
        glColor3f(*GREEN)
        
        parts = [(0, 0, 0, 0.3, 0.8, 0.2), (0, 0.6, 0, 0.2, 0.2, 0.2), (-0.25, 0.2, 0, 0.1, 0.5, 0.1),
                (0.25, 0.2, 0, 0.1, 0.5, 0.1), (-0.1, -0.6, 0, 0.1, 0.6, 0.1), (0.1, -0.6, 0, 0.1, 0.6, 0.1)]
        
        for i, (x, y, z, sx, sy, sz) in enumerate(parts):
            glPushMatrix()
            glTranslatef(x, y, z)
            if i == 1:  
                glutSolidSphere(0.2, 8, 8)
            else:
                glScalef(sx, sy, sz)
                glutSolidCube(1.0)
            glPopMatrix()
        
        glColor3f(1, 1, 1)
        glPushMatrix()
        glTranslatef(0, 0.8, 0.3)  
        glScalef(0.1, 0.1, 0.3)
        glutSolidCone(1.0, 1.0, 4, 1)
        glPopMatrix()
        glPopMatrix()

class Wall:
    def __init__(self, x, y, z, sx, sy, sz):
        self.position = Vector3(x, y, z)
        self.size = Vector3(sx, sy, sz)
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(*GRAY)
        glScalef(self.size.x, self.size.y, self.size.z)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(0.2, 0.2, 0.2)
        glScalef(self.size.x, self.size.y, self.size.z)
        glutWireCube(1)
        glPopMatrix()





class SecurityCamera:
    def __init__(self, x, z, direction=1):
        self.position = Vector3(x, 2.0, z)
        self.base_position = Vector3(x, 0, z)
        self.angle = 0  
        self.direction = direction
        self.range = 5
        self.fov_degrees = 60
        self.disabled = False
        
        self.detection_time = 0.0
        self.detection_threshold = 2.0
        self.is_detecting = False
        self.detection_start_time = 0.0
        
        self.rotation_timer = 0.0  
        self.rotation_interval = 5.0 
        self.target_angle = 0.0  
        self.rotating = False  
        self.rotation_speed = math.pi / 2  
        
    def update(self):
        if not self.disabled:
            import time
            current_time = time.time()
            if hasattr(self, 'last_update_time'):
                dt = current_time - self.last_update_time
            else:
                dt = 0.016  
            self.last_update_time = current_time
            
            if not self.rotating:
                self.rotation_timer += dt
                if self.rotation_timer >= self.rotation_interval:
                    self.rotating = True
                    self.target_angle = self.angle + math.pi / 2  
                    self.rotation_timer = 0.0
            else:
                angle_diff = self.target_angle - self.angle
                
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                rotation_step = self.rotation_speed * dt
                if abs(angle_diff) <= rotation_step:
                    self.angle = self.target_angle
                    self.rotating = False
                else:
                    self.angle += rotation_step * (1 if angle_diff > 0 else -1)
                
                self.angle = self.angle % (2 * math.pi)
            
    def can_see_player(self, player, walls):
        if self.disabled:
            return False
            
        dx = player.position.x - self.position.x
        dz = player.position.z - self.position.z
        distance = math.sqrt(dx * dx + dz * dz)
        
        if distance > self.range:
            return False
        
        cos_angle = math.cos(self.angle)
        sin_angle = math.sin(self.angle)
        
        local_x = dx * cos_angle - dz * sin_angle 
        local_z = dx * sin_angle + dz * cos_angle  

        if local_x <= 0:  
            return False
            
        angle_from_center = math.atan2(abs(local_z), local_x)
        fov_half_radians = math.radians(self.fov_degrees / 2)
        
        if angle_from_center <= fov_half_radians:
            return self.has_clear_line_of_sight(player, walls)
            
        return False
    
    def has_clear_line_of_sight(self, player, walls):
        camera_x, camera_z = self.position.x, self.position.z
        player_x, player_z = player.position.x, player.position.z
        
        for wall in walls:
            if self.line_intersects_wall(camera_x, camera_z, player_x, player_z, wall):
                return False
        return True
        
    def line_intersects_wall(self, x1, z1, x2, z2, wall):
        wall_left = wall.position.x - wall.size.x / 2
        wall_right = wall.position.x + wall.size.x / 2
        wall_top = wall.position.z - wall.size.z / 2
        wall_bottom = wall.position.z + wall.size.z / 2

        if ((x1 < wall_left and x2 > wall_right) or (x1 > wall_right and x2 < wall_left)):
            t = (wall.position.x - x1) / (x2 - x1) if x2 != x1 else 0
            z_intersect = z1 + t * (z2 - z1)
            if wall_top <= z_intersect <= wall_bottom:
                return True
                
        if ((z1 < wall_top and z2 > wall_bottom) or (z1 > wall_bottom and z2 < wall_top)):
            t = (wall.position.z - z1) / (z2 - z1) if z2 != z1 else 0
            x_intersect = x1 + t * (x2 - x1)
            if wall_left <= x_intersect <= wall_right:
                return True
                
        return False
    
    def update_detection(self, player, walls):
        current_time = time.time()
        player_visible = self.can_see_player(player, walls)
        
        if player_visible:
            if not self.is_detecting:
                self.is_detecting = True
                self.detection_start_time = current_time
                self.detection_time = 0.0
                return 'detecting'
            else:
                self.detection_time = current_time - self.detection_start_time
                detection_progress = self.detection_time / self.detection_threshold
                
                if detection_progress >= 0.8:
                    return 'alarm'
                else:
                    return 'detecting'
        else:
            if self.is_detecting:
                self.is_detecting = False
                self.detection_time = 0.0
                self.detection_start_time = 0.0
            return 'none'
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.base_position.x, 0.15, self.base_position.z)
        glColor3f(0.4, 0.4, 0.4) if not self.disabled else glColor3f(0.2, 0.2, 0.2)
        glScalef(0.6, 0.3, 0.6)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(self.base_position.x, 1.0, self.base_position.z)
        glColor3f(0.5, 0.5, 0.5) if not self.disabled else glColor3f(0.3, 0.3, 0.3)
        glScalef(0.1, 2.0, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        if self.disabled:
            glColor3f(0.3, 0.3, 0.3)
        elif self.is_detecting:
            detection_progress = min(self.detection_time / self.detection_threshold, 1.0)
            glColor3f(1.0, 1.0 - detection_progress, 0.0)
        else:
            glColor3f(0.6, 0, 0)
            
        glScalef(0.8, 0.5, 0.8)
        glutSolidCube(1.0)
        glPopMatrix()
        
        if not self.disabled:
            glPushMatrix()
            glTranslatef(self.position.x, self.position.y, self.position.z)
            glRotatef(math.degrees(self.angle), 0, 1, 0)
            
            if self.is_detecting:
                glColor4f(1, 0.5, 0, 0.6)
            else:
                glColor4f(1, 0, 0, 0.4)
                
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_LIGHTING)
            
            glBegin(GL_TRIANGLES)
            num_segments = 16
            for i in range(num_segments):
                angle1 = math.radians(-self.fov_degrees/2 + (i * self.fov_degrees / num_segments))
                angle2 = math.radians(-self.fov_degrees/2 + ((i + 1) * self.fov_degrees / num_segments))
                
                glVertex3f(0, 0, 0)  
                glVertex3f(self.range * math.cos(angle1), -2.0, self.range * math.sin(angle1))
                glVertex3f(self.range * math.cos(angle2), -2.0, self.range * math.sin(angle2))
            glEnd()
            
            glColor3f(1, 0, 0)
            glLineWidth(2.0)
            glBegin(GL_LINES)
            fov_half = math.radians(self.fov_degrees / 2)
            glVertex3f(0, 0, 0)
            glVertex3f(self.range * math.cos(-fov_half), -2.0, self.range * math.sin(-fov_half))
            glVertex3f(0, 0, 0)
            glVertex3f(self.range * math.cos(fov_half), -2.0, self.range * math.sin(fov_half))
            
            glColor3f(1, 1, 1)
            glVertex3f(0, 0, 0)
            glVertex3f(self.range, -2.0, 0)
            glEnd()
            glLineWidth(1.0)
            
            glEnable(GL_LIGHTING)
            glDisable(GL_BLEND)
            glPopMatrix()




class Laser:
    def __init__(self, x1, z1, x2, z2, movement_type='static'):
        self.original_start, self.original_end = Vector3(x1, 0, z1), Vector3(x2, 0, z2)
        self.start, self.end = Vector3(x1, 0, z1), Vector3(x2, 0, z2)
        self.active = True
        self.movement_type = movement_type
        self.movement_speed, self.movement_time, self.movement_range = 0.02, 0, 3.0
        self.rotation_center = Vector3((x1 + x2) / 2, 0, (z1 + z2) / 2)
        self.swing_angle = 0
        self.original_length = math.sqrt((x2 - x1)**2 + (z2 - z1)**2)
        self.original_angle = math.atan2(z2 - z1, x2 - x1)
    
    def update(self):
        self.movement_time += self.movement_speed
        
        if self.movement_type == 'rotating':
            angle = self.original_angle + self.movement_time
            half_length = self.original_length / 2
            center_x, center_z = self.rotation_center.x, self.rotation_center.z
            self.start.x = center_x - half_length * math.cos(angle)
            self.start.z = center_z - half_length * math.sin(angle)
            self.end.x = center_x + half_length * math.cos(angle)
            self.end.z = center_z + half_length * math.sin(angle)
            
        elif self.movement_type == 'sliding':
            slide_offset = math.sin(self.movement_time) * self.movement_range
            perp_angle = self.original_angle + math.pi / 2
            offset_x, offset_z = slide_offset * math.cos(perp_angle), slide_offset * math.sin(perp_angle)
            self.start.x, self.start.z = self.original_start.x + offset_x, self.original_start.z + offset_z
            self.end.x, self.end.z = self.original_end.x + offset_x, self.original_end.z + offset_z
            
        elif self.movement_type in ['horizontal_fixed', 'vertical_fixed']:
            offset = math.sin(self.movement_time) * self.movement_range
            self.start.x, self.start.z = self.original_start.x, self.original_start.z
            if self.movement_type == 'horizontal_fixed':
                self.end.x, self.end.z = self.original_end.x, self.original_end.z + offset
            else:
                self.end.x, self.end.z = self.original_end.x + offset, self.original_end.z
    
    def check_collision(self, player):
        if not self.active:
            return False
        if player.position.y > 0.8: 
            return False
            
        px, pz = player.position.x, player.position.z
        x1, z1, x2, z2 = self.start.x, self.start.z, self.end.x, self.end.z
        A, B, C = z2 - z1, x1 - x2, x2 * z1 - x1 * z2
        distance = abs(A * px + B * pz + C) / math.sqrt(A * A + B * B)
        if distance < 0.3:
            min_x, max_x, min_z, max_z = min(x1, x2), max(x1, x2), min(z1, z2), max(z1, z2)
            return px >= min_x - 0.3 and px <= max_x + 0.3 and pz >= min_z - 0.3 and pz <= max_z + 0.3
        return False
    
    def draw(self):
        if not self.active:
            return
        for pos in [self.start, self.end]:
            glPushMatrix()
            glTranslatef(pos.x, pos.y + 0.05, pos.z)  
            glColor3f(*ORANGE)
            glutSolidCube(0.3)
            glPopMatrix()
        glColor3f(*RED)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex3f(self.start.x, self.start.y + 0.05, self.start.z)  
        glVertex3f(self.end.x, self.end.y + 0.05, self.end.z)  
        glEnd()
        glLineWidth(1.0)

class Terminal:
    def __init__(self, x, z, terminal_type):
        self.position = Vector3(x, 0.75, z)
        self.hacked = False
        self.type = terminal_type
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        if self.hacked:
            glColor3f(*GREEN)
        else:
            glColor3f(*RED) if self.type == 'camera' else glColor3f(*ORANGE)
        
        glScalef(1.0, 1.5, 0.3)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y - 0.5, self.position.z)
        glColor3f(0.3, 0.3, 0.3)
        glScalef(0.8, 0.5, 0.6)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y + 0.2, self.position.z + 0.16)
        if self.hacked:
            glColor3f(0.8, 1, 0.8)
        else:
            glColor3f(1, 0.6, 0.6) if self.type == 'camera' else glColor3f(1, 0.8, 0.6)
        glScalef(0.8, 1.0, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(self.position.x + 0.3, self.position.y + 0.6, self.position.z + 0.16)
        if self.hacked:
            glColor3f(0, 1, 0)
        else:
            glColor3f(1, 0, 0) if self.type == 'camera' else glColor3f(1, 0.5, 0)
        glutSolidSphere(0.1, 6, 6)
        glPopMatrix()

class Objective:
    def __init__(self, x, z):
        self.position = Vector3(x, 1, z)
        self.pulse_time = 0
    
    def update(self):
        pass
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(*GREEN)
        
        diamond_size = 0.5
        glEnable(GL_LIGHTING)
        
        top = (0, diamond_size, 0)
        corners = [(diamond_size, 0, 0), (0, 0, diamond_size), (-diamond_size, 0, 0), (0, 0, -diamond_size)]
        
        glBegin(GL_TRIANGLES)
        for i in range(4):
            next_i = (i + 1) % 4
            glNormal3f(0, 1, 0)
            glVertex3f(*top)
            glVertex3f(*corners[i])
            glVertex3f(*corners[next_i])
        
        bottom = (0, -diamond_size, 0)
        for i in range(4):
            next_i = (i + 1) % 4
            glNormal3f(0, -1, 0)
            glVertex3f(*bottom)
            glVertex3f(*corners[next_i])
            glVertex3f(*corners[i])
        glEnd()
        
        glDisable(GL_LIGHTING)
        glColor3f(0.8, 1.0, 0.8)
        glLineWidth(2.0)
        
        glBegin(GL_LINES)
        for corner in corners:
            glVertex3f(*top)
            glVertex3f(*corner)
        for corner in corners:
            glVertex3f(*bottom)
            glVertex3f(*corner)
        for i in range(4):
            next_i = (i + 1) % 4
            glVertex3f(*corners[i])
            glVertex3f(*corners[next_i])
        glEnd()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        glPopMatrix()

class Game:
    def __init__(self):
        self.state, self.level, self.score = 'playing', 1, 0
        self.time_left, self.start_time = 120, time.time()
        self.keys, self.hacking = {}, False
        self.hack_sequence, self.hack_attempts, self.hack_target, self.hack_input = "", 0, None, ""
        self.hack_lives = 2
        self.camera_distance = 15
        self.first_person_mode = False 
        
        self.player = Player()
        self.walls, self.cameras, self.lasers, self.terminals = [], [], [], []
        self.objective = None
        self.create_level(self.level)
        
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [10, 20, 10, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1])
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(75, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(0.0, 0.0, 0.0, 1.0)
    
    def create_level(self, level_num):
        self.walls.clear()
        self.cameras.clear()
        self.lasers.clear()
        self.terminals.clear()
        
        wall_positions = [(0, 1.5, -10, 20, 3, 1), (0, 1.5, 10, 20, 3, 1), (-10, 1.5, 0, 1, 3, 20), 
                         (10, 1.5, 0, 1, 3, 20), (-3, 1.5, -3, 1, 3, 6), (3, 1.5, 3, 6, 3, 1), (6, 1.5, -6, 4, 3, 1)]
        self.walls = [Wall(*pos) for pos in wall_positions]
        
        base_camera_positions = [(-6, -6, 1), (6, 0, -1), (0, 6, 1), (-2, 2, 1), (4, -4, -1), (-7, 3, 1), (2, -7, -1), (8, -2, 1)]
        cameras_to_add = min(level_num, len(base_camera_positions))
        self.cameras = [SecurityCamera(*base_camera_positions[i]) for i in range(cameras_to_add)]
        
        base_laser_configs = [(-1, -1, 1, -1, 'horizontal_fixed'), (4, -4, 4, -2, 'vertical_fixed'), (-4, 4, -2, 4, 'horizontal_fixed'), 
                             (-6, -6, -6, -4, 'vertical_fixed'), (6, 2, 8, 2, 'horizontal_fixed'), (0, -8, 2, -8, 'horizontal_fixed'), 
                             (-8, 0, -8, 2, 'vertical_fixed'), (7, -3, 7, -1, 'vertical_fixed')]
        lasers_to_add = min(1 + level_num, len(base_laser_configs))
        self.lasers = [Laser(*base_laser_configs[i]) for i in range(lasers_to_add)]
        
        self.terminals = [Terminal(-7, 7, 'camera'), Terminal(7, -7, 'laser')]
        self.objective = Objective(8, 8)
    
    def update_camera(self):
        glLoadIdentity()
        
        if self.first_person_mode:
            cam_x = self.player.position.x
            cam_y = self.player.position.y + 0.4  
            cam_z = self.player.position.z
            look_distance = 10
            look_x = cam_x + look_distance * math.sin(math.radians(self.player.rotation))
            look_y = cam_y
            look_z = cam_z + look_distance * math.cos(math.radians(self.player.rotation)) 
            
            gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
        else:
            cam_x = self.player.position.x
            cam_y = self.camera_distance
            cam_z = self.player.position.z + 3
            look_x, look_y, look_z = self.player.position.x, 0, self.player.position.z
            gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
    
    def update(self):
        if self.state == 'playing':
            elapsed = time.time() - self.start_time
            self.time_left = max(0, 120 - int(elapsed))
            if self.time_left <= 0:
                self.game_over("TIME LIMIT EXCEEDED")
                return
            
            self.player.update(self.keys, self.walls)
            
            cameras_disabled = any(t.hacked and t.type == 'camera' for t in self.terminals)
            if not cameras_disabled:
                for i, camera in enumerate(self.cameras):
                    camera.update()
                    detection_status = camera.update_detection(self.player, self.walls)
                    
                    if detection_status == 'alarm':
                        self.game_over("CAUGHT IN CAMERA'S RED VISION CONE!")
                        return
                    elif detection_status == 'detecting':
                        pass
            else:
                for camera in self.cameras:
                    camera.disabled = True
                    camera.update()
            
            for laser in self.lasers:
                laser.update()
            
            lasers_disabled = any(t.hacked and t.type == 'laser' for t in self.terminals)
            if not lasers_disabled:
                for laser in self.lasers:
                    if laser.check_collision(self.player):
                        self.game_over("HIT BY LASER SECURITY")
                        return
            else:
                for laser in self.lasers:
                    laser.active = False
            
            self.objective.update()
            
            if self.player.position.distance_to(self.objective.position) < 1.5:
                if all(terminal.hacked for terminal in self.terminals):
                    self.win_level()
                else:
                    camera_terminal_hacked = any(t.hacked and t.type == 'camera' for t in self.terminals)
                    laser_terminal_hacked = any(t.hacked and t.type == 'laser' for t in self.terminals)
                    if not camera_terminal_hacked and not laser_terminal_hacked:
                        print("Need to hack BOTH terminals: Camera (Red) and Laser (Orange)")
                    elif not camera_terminal_hacked:
                        print("Still need to hack the Camera terminal (Red)")
                    elif not laser_terminal_hacked:
                        print("Still need to hack the Laser terminal (Orange)")
    
    def try_hack(self):
        nearest_terminal = None
        min_distance = float('inf')
        for terminal in self.terminals:
            if not terminal.hacked:
                distance = self.player.position.distance_to(terminal.position)
                if distance < min_distance and distance < 2:
                    min_distance = distance
                    nearest_terminal = terminal
        if nearest_terminal:
            self.start_hacking(nearest_terminal)
    
    def start_hacking(self, terminal):
        self.hacking, self.state, self.hack_target, self.hack_input = True, 'hacking', terminal, ""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        sequence_length = random.randint(4, 6)
        self.hack_sequence = ''.join(random.choice(chars) for _ in range(sequence_length))
        terminal_name = "CAMERA CONTROL" if terminal.type == 'camera' else "LASER CONTROL"
        print(f"HACKING {terminal_name} TERMINAL")
        print(f"Enter sequence: {self.hack_sequence}")
        print(f"Hack Lives Remaining: {self.hack_lives}")
        print(f"Current input: {self.hack_input}")
    
    def submit_hack(self, input_sequence):
        if input_sequence.upper() == self.hack_sequence:
            self.score += 500
            self.hack_target.hacked = True
            if self.hack_target.type == 'camera':
                for camera in self.cameras:
                    camera.disabled = True
                print("CAMERA SYSTEM DISABLED! All cameras are now offline.")
            else:
                for laser in self.lasers:
                    laser.active = False
                print("LASER SYSTEM DISABLED! All laser barriers are now offline.")
            print("HACK SUCCESSFUL!")
            self.cancel_hack()
        else:
            self.hack_lives -= 1
            print(f"INCORRECT SEQUENCE! Lives remaining: {self.hack_lives}")
            print(f"Target sequence: {self.hack_sequence}")
            
            if self.hack_lives <= 0:
                self.cancel_hack()
                self.game_over("OUT OF HACKING LIVES - MISSION FAILED")
            else:
                print(f"Try again! You have {self.hack_lives} lives left for all terminal hacking.")
                self.hack_input = ""
    
    def cancel_hack(self):
        self.hacking, self.state, self.hack_target, self.hack_input = False, 'playing', None, ""
        print("Hacking cancelled.")
    
    def game_over(self, reason):
        self.state = 'game_over'
        print(f"MISSION FAILED: {reason}\nPress R to restart or ESC to exit")
    
    def win_level(self):
        self.state = 'won'
        time_bonus = max(0, self.time_left * 10)
        self.score += time_bonus
        print(f"MISSION COMPLETE! Score: {self.score}, Time Bonus: {time_bonus}\nPress N for next level or R to restart")
    
    def next_level(self):
        self.level += 1
        self.time_left = max(90, 120 - (self.level - 1) * 10)
        self.start_time = time.time()-10
        self.state = 'playing'
        self.hack_lives = 2
        self.player.position = Vector3(-8, 0.5, -8)
        self.create_level(self.level)
        print(f"Level {self.level} started!\nCameras: {len(self.cameras)}, Lasers: {len(self.lasers)}")
        print(f"Hack Lives: {self.hack_lives}")
    
    def restart_game(self):
        self.level, self.score = 1, 0
        self.time_left, self.start_time, self.state = 120, time.time(), 'playing'
        self.hack_lives = 2 
        self.player.position = Vector3(-8, 0.5, -8)
        self.create_level(self.level)
        print(f"Game restarted!\nLevel {self.level}: Cameras: {len(self.cameras)}, Lasers: {len(self.lasers)}")
        print(f"Hack Lives: {self.hack_lives}")
    
    def draw_floor(self):
        glColor3f(*DARK_GRAY)
        glBegin(GL_QUADS)
        glVertex3f(-10, 0, -10)
        glVertex3f(10, 0, -10)
        glVertex3f(10, 0, 10)
        glVertex3f(-10, 0, 10)
        glEnd()
        
        glColor3f(0.3, 0.3, 0.3)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for i in range(-10, 11, 2):
            glVertex3f(i, 0.01, -10)
            glVertex3f(i, 0.01, 10)
            glVertex3f(-10, 0.01, i)
            glVertex3f(10, 0.01, i)
        glEnd()
        
        glColor3f(0.5, 0.5, 0.5)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex3f(-1, 0.02, 0)
        glVertex3f(1, 0.02, 0)
        glVertex3f(0, 0.02, -1)
        glVertex3f(0, 0.02, 1)
        glEnd()
        glLineWidth(1.0)
    
    def draw_text(self, x, y, text, color=None):
        if GLUT_BITMAP_HELVETICA_18 is None:
            return
        if color:
            glColor3f(*color)
        else:
            glColor3f(1, 1, 1)
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    def draw_ui(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        texts = [f"Level: {self.level}", f"Score: {self.score}", f"Time: {self.time_left}",
                f"Hack Lives: {self.hack_lives}",
                f"Cameras: {len(self.cameras)} | Lasers: {len(self.lasers)}"]
        
        camera_terminal_hacked = any(t.hacked and t.type == 'camera' for t in self.terminals)
        laser_terminal_hacked = any(t.hacked and t.type == 'laser' for t in self.terminals)
        
        detecting_cameras = []
        if not camera_terminal_hacked:
            for i, camera in enumerate(self.cameras):
                if camera.is_detecting:
                    detection_progress = min(camera.detection_time / camera.detection_threshold, 1.0)
                    detecting_cameras.append((i+1, detection_progress))
        
        texts.extend([f"Camera System: {'OFFLINE' if camera_terminal_hacked else 'ACTIVE'}",
                     f"Laser System: {'OFFLINE' if laser_terminal_hacked else 'ACTIVE'}"])
        
        if detecting_cameras:
            for cam_id, progress in detecting_cameras:
                if progress >= 0.8:
                    warning_level = "ALARM TRIGGERED!"
                elif progress >= 0.6:
                    warning_level = "CRITICAL DANGER"
                elif progress >= 0.4:
                    warning_level = "DANGER"
                elif progress >= 0.2:
                    warning_level = "WARNING"
                else:
                    warning_level = "DETECTED"
                texts.append(f"Camera {cam_id}: {warning_level} - {progress*100:.0f}%")
        
        for i, text in enumerate(texts):
            if "Camera" in text and any(word in text for word in ["DETECTED", "WARNING", "DANGER", "ALARM"]):
                if "ALARM TRIGGERED!" in text:
                    glColor3f(1, 0, 0)  
                elif "DANGER" in text:
                    glColor3f(1, 0.3, 0) 
                elif "WARNING" in text:
                    glColor3f(1, 0.5, 0)  
                else:
                    glColor3f(1, 1, 0)  
            else:
                glColor3f(1, 1, 1)  
            self.draw_text(20, 30 + i * 20, text)
        
        if self.hacking:
            hack_type = "CAMERA CONTROL" if self.hack_target.type == 'camera' else "LASER CONTROL"
            hack_texts = [f"HACKING {hack_type}", "HACKING...", f"Enter: {self.hack_sequence}", f"Input: {self.hack_input}"]
            for i, text in enumerate(hack_texts):
                glColor3f(1, 1, 1) 
                self.draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 70 + i * 30, text)
        
        if self.state == 'game_over':
            glColor3f(1, 0, 0)
            self.draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, "MISSION FAILED!")
            glColor3f(1, 1, 1)
            self.draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 30, "Press R to restart")
        
        if self.state == 'won':
            glColor3f(0, 1, 0)  
            self.draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, "MISSION COMPLETE!")
            glColor3f(1, 1, 1)
            self.draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 30, "Press N for next level")
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.update_camera()
        self.draw_floor()
        
        objects_to_draw = self.walls + self.cameras + self.lasers + self.terminals + [self.objective]
        if not self.first_person_mode:
            objects_to_draw.append(self.player)
            
        for obj in objects_to_draw:
            obj.draw()
        
        self.draw_ui()
        glutSwapBuffers()

game = None
FRAME_INTERVAL = 1.0 / FPS
_last_frame_time = 0.0

def _handle_sigint(sig, frame):
    print("\nCtrl+C detected, shutting down cleanly...")
    try:
        glutLeaveMainLoop()
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, _handle_sigint)

def display():
    game.update()
    game.render()

def idle():
    global _last_frame_time
    now = time.time()
    if now - _last_frame_time >= FRAME_INTERVAL:
        glutPostRedisplay()
        _last_frame_time = now

def keyboard(key, x, y):
    game.keys[key] = True
    
    if key == b'e' or key == b'E':
        if not game.hacking:
            game.try_hack()
            return
    elif key == b'\x1b':
        if game.hacking:
            game.cancel_hack()
        else:
            sys.exit(0)
    elif key == b'r' or key == b'R':
        if game.state == 'game_over':
            game.restart_game()
        elif game.state == 'won':
            game.next_level() 
    elif key == b'n' or key == b'N':
        if game.state == 'won':
            game.next_level() 
    
    if game.hacking and key.isalnum():
        char = key.decode('ascii').upper()
        game.hack_input += char
        print(f"Input: {game.hack_input}")
        
        if len(game.hack_input) >= len(game.hack_sequence):
            game.submit_hack(game.hack_input)
            game.hack_input = ""

def mouse(button, state, x, y):
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        game.first_person_mode = not game.first_person_mode
        mode_text = "first-person" if game.first_person_mode else "third-person"
        print(f"Camera switched to {mode_text} mode")

def keyboard_up(key, x, y):
    if key in game.keys:
        game.keys[key] = False

def special_keys(key, x, y):
    special_map = {GLUT_KEY_UP: 'up', GLUT_KEY_DOWN: 'down', GLUT_KEY_LEFT: 'left', GLUT_KEY_RIGHT: 'right'}
    if key in special_map:
        game.keys[special_map[key]] = True

def special_keys_up(key, x, y):
    special_map = {GLUT_KEY_UP: 'up', GLUT_KEY_DOWN: 'down', GLUT_KEY_LEFT: 'left', GLUT_KEY_RIGHT: 'right'}
    if key in special_map:
        game.keys[special_map[key]] = False

def main():
    global game
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Cyber Heist 3D - Strategic Terminal System")
    
    game = Game()
    game.init_opengl()
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutSpecialUpFunc(special_keys_up)
    glutMouseFunc(mouse)  
    glutIdleFunc(idle)

    print("CYBER HEIST 3D - STRATEGIC TERMINAL SYSTEM")
    print("Controls:\nWASD - Move Forward/Back & Rotate Left/Right\nSPACE - Jump\nE - Hack terminal (when near)")
    print("R - Restart/Next level\nESC - Cancel hacking / Exit\nRIGHT-CLICK - Toggle First/Third Person Camera")
    print("\nSTRATEGIC GAMEPLAY:")
    print("RED Terminal - Disables ALL security cameras")
    print("ORANGE Terminal - Disables ALL laser barriers")
    print("Strategy tip: Disable cameras first for stealth, or lasers first for mobility")
    print("\nProgressive Difficulty:\nLevel 1: 1 camera, 2 lasers\nEach level: +1 camera, +1 laser")
    print("WARNING: Don't touch red camera light cones or laser barriers!")
    
    glutMainLoop()
        

if __name__ == "__main__":
    main()