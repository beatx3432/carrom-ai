import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carrom AI - Stable Physics")

clock = pygame.time.Clock()

# --------------------------------------------------
# Board
# --------------------------------------------------

LEFT = 80
TOP = 80
RIGHT = 720
BOTTOM = 720

WOOD = (210, 160, 95)
DARK_WOOD = (120, 75, 35)

BLACK = (20, 20, 20)
WHITE = (245, 245, 245)
BLUE = (40, 100, 220)

RED = (200, 30, 30)
GREEN = (0, 255, 0)
YELLOW = (255, 220, 0)

# --------------------------------------------------
# Sizes
# --------------------------------------------------

COIN_RADIUS = 12
STRIKER_RADIUS = 18
POCKET_RADIUS = 35

# --------------------------------------------------
# Physics
# --------------------------------------------------

STRIKER_SPEED = 7.0
SHOT_POWER = 10.0

FRICTION = 0.995
BOUNCE = 0.95
COLLISION_BOUNCE = 0.90

STOP_SPEED = 0.12

# --------------------------------------------------
# Pockets
# --------------------------------------------------

pockets = [
    [80.0, 80.0],
    [720.0, 80.0],
    [80.0, 720.0],
    [720.0, 720.0]
]

# --------------------------------------------------
# Coins
# --------------------------------------------------

coins = [
    [370.0, 400.0],
    [430.0, 400.0],
    [400.0, 370.0],
    [400.0, 430.0],
    [380.0, 380.0],
    [420.0, 420.0]
]

coin_velocities = []

for _ in coins:
    coin_velocities.append([0.0, 0.0])

# --------------------------------------------------
# Striker
# --------------------------------------------------

striker = [400.0, 680.0]

# --------------------------------------------------
# Current shot
# --------------------------------------------------

selected_shot = None
active_coin_index = None

shooting = False
coin_moving = False
waiting_for_next_shot = True

# --------------------------------------------------
# Cushions
# --------------------------------------------------

cushions = {
    "LEFT": LEFT + COIN_RADIUS,
    "RIGHT": RIGHT - COIN_RADIUS,
    "TOP": TOP + COIN_RADIUS,
    "BOTTOM": BOTTOM - COIN_RADIUS
}


# ==================================================
# DIRECT SHOT
# ==================================================

def calculate_direct_shot(coin, pocket):

    dx = pocket[0] - coin[0]
    dy = pocket[1] - coin[1]

    distance = math.sqrt(dx * dx + dy * dy)

    if distance <= 0:
        return None

    return {
        "type": "DIRECT",
        "wall": None,
        "bounce": None,
        "distance": distance,
        "direction": [
            dx / distance,
            dy / distance
        ]
    }


# ==================================================
# BANK SHOTS
# ==================================================

def calculate_bank_shots(coin, pocket):

    candidates = []

    cx, cy = coin
    px, py = pocket

    # ----------------------------------------------
    # RIGHT
    # ----------------------------------------------

    wall_x = cushions["RIGHT"]

    rx = 2 * wall_x - px
    ry = py

    dx = rx - cx
    dy = ry - cy

    if abs(dx) > 0.001:

        t = (wall_x - cx) / dx
        bounce_y = cy + dy * t

        if 0 < t < 1:

            if TOP + COIN_RADIUS < bounce_y < BOTTOM - COIN_RADIUS:

                candidates.append({
                    "type": "BANK",
                    "wall": "RIGHT",
                    "bounce": [wall_x, bounce_y],
                    "distance": math.sqrt(dx * dx + dy * dy)
                })

    # ----------------------------------------------
    # LEFT
    # ----------------------------------------------

    wall_x = cushions["LEFT"]

    rx = 2 * wall_x - px
    ry = py

    dx = rx - cx
    dy = ry - cy

    if abs(dx) > 0.001:

        t = (wall_x - cx) / dx
        bounce_y = cy + dy * t

        if 0 < t < 1:

            if TOP + COIN_RADIUS < bounce_y < BOTTOM - COIN_RADIUS:

                candidates.append({
                    "type": "BANK",
                    "wall": "LEFT",
                    "bounce": [wall_x, bounce_y],
                    "distance": math.sqrt(dx * dx + dy * dy)
                })

    # ----------------------------------------------
    # TOP
    # ----------------------------------------------

    wall_y = cushions["TOP"]

    rx = px
    ry = 2 * wall_y - py

    dx = rx - cx
    dy = ry - cy

    if abs(dy) > 0.001:

        t = (wall_y - cy) / dy
        bounce_x = cx + dx * t

        if 0 < t < 1:

            if LEFT + COIN_RADIUS < bounce_x < RIGHT - COIN_RADIUS:

                candidates.append({
                    "type": "BANK",
                    "wall": "TOP",
                    "bounce": [bounce_x, wall_y],
                    "distance": math.sqrt(dx * dx + dy * dy)
                })

    # ----------------------------------------------
    # BOTTOM
    # ----------------------------------------------

    wall_y = cushions["BOTTOM"]

    rx = px
    ry = 2 * wall_y - py

    dx = rx - cx
    dy = ry - cy

    if abs(dy) > 0.001:

        t = (wall_y - cy) / dy
        bounce_x = cx + dx * t

        if 0 < t < 1:

            if LEFT + COIN_RADIUS < bounce_x < RIGHT - COIN_RADIUS:

                candidates.append({
                    "type": "BANK",
                    "wall": "BOTTOM",
                    "bounce": [bounce_x, wall_y],
                    "distance": math.sqrt(dx * dx + dy * dy)
                })

    return candidates


# ==================================================
# CHOOSE SHOT
# ==================================================

def choose_best_shot():

    candidates = []

    for coin_index, coin in enumerate(coins):

        for pocket_index, pocket in enumerate(pockets):

            # Direct
            direct = calculate_direct_shot(
                coin,
                pocket
            )

            if direct:

                shot = direct.copy()

                shot["coin_index"] = coin_index
                shot["pocket_index"] = pocket_index

                candidates.append(shot)

            # Bank
            for bank in calculate_bank_shots(
                coin,
                pocket
            ):

                shot = bank.copy()

                shot["coin_index"] = coin_index
                shot["pocket_index"] = pocket_index

                candidates.append(shot)

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda shot: shot["distance"]
    )


# ==================================================
# PREPARE SHOT
# ==================================================

def prepare_shot():

    global selected_shot
    global active_coin_index
    global shooting
    global waiting_for_next_shot

    selected_shot = choose_best_shot()

    if selected_shot is None:
        return

    active_coin_index = selected_shot["coin_index"]

    target_coin = coins[active_coin_index]

    target_pocket = pockets[
        selected_shot["pocket_index"]
    ]

    direction = selected_shot["direction"]

    hit_point = [
        target_coin[0] - direction[0] * 30,
        target_coin[1] - direction[1] * 30
    ]

    selected_shot["hit_point"] = hit_point
    selected_shot["target_coin"] = target_coin[:]
    selected_shot["target_pocket"] = target_pocket[:]

    striker[0] = 400.0
    striker[1] = 680.0

    shooting = True
    waiting_for_next_shot = False

    print()
    print("------------------------------")
    print("NEW AI SHOT")
    print("Coin:", active_coin_index + 1)
    print(
        "Pocket:",
        selected_shot["pocket_index"] + 1
    )
    print("Type:", selected_shot["type"])

    if selected_shot["type"] == "BANK":

        print(
            "Cushion:",
            selected_shot["wall"]
        )

        print(
            "Bounce:",
            round(selected_shot["bounce"][0], 1),
            round(selected_shot["bounce"][1], 1)
        )

    print("------------------------------")


# ==================================================
# STABLE COIN COLLISIONS
# ==================================================

def handle_coin_collisions():

    for i in range(len(coins)):

        for j in range(i + 1, len(coins)):

            a = coins[i]
            b = coins[j]

            dx = b[0] - a[0]
            dy = b[1] - a[1]

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            minimum_distance = COIN_RADIUS * 2

            if distance <= 0:
                continue

            if distance < minimum_distance:

                nx = dx / distance
                ny = dy / distance

                # Separate coins completely
                overlap = minimum_distance - distance

                a[0] -= nx * (overlap / 2 + 0.1)
                a[1] -= ny * (overlap / 2 + 0.1)

                b[0] += nx * (overlap / 2 + 0.1)
                b[1] += ny * (overlap / 2 + 0.1)

                rvx = (
                    coin_velocities[j][0]
                    - coin_velocities[i][0]
                )

                rvy = (
                    coin_velocities[j][1]
                    - coin_velocities[i][1]
                )

                velocity_normal = (
                    rvx * nx
                    + rvy * ny
                )

                # Only collide when moving toward each other
                if velocity_normal < 0:

                    impulse = (
                        -velocity_normal
                        * COLLISION_BOUNCE
                    )

                    coin_velocities[i][0] -= (
                        impulse * nx
                    )

                    coin_velocities[i][1] -= (
                        impulse * ny
                    )

                    coin_velocities[j][0] += (
                        impulse * nx
                    )

                    coin_velocities[j][1] += (
                        impulse * ny
                    )

                    print(
                        ">>> COIN COLLISION:",
                        i + 1,
                        "<->",
                        j + 1
                    )


# ==================================================
# REMOVE POCKETED COINS
# ==================================================

def check_pockets():

    global active_coin_index

    for i in range(len(coins) - 1, -1, -1):

        coin = coins[i]

        for pocket in pockets:

            dx = coin[0] - pocket[0]
            dy = coin[1] - pocket[1]

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance <= POCKET_RADIUS:

                print(
                    "COIN POCKETED:",
                    i + 1
                )

                coins.pop(i)
                coin_velocities.pop(i)

                if active_coin_index is not None:

                    if i == active_coin_index:

                        active_coin_index = None

                    elif i < active_coin_index:

                        active_coin_index -= 1

                return True

    return False


# ==================================================
# MAIN LOOP
# ==================================================

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

    # ------------------------------------------------
    # Prepare next shot
    # ------------------------------------------------

    if (
        waiting_for_next_shot
        and not shooting
        and not coin_moving
    ):

        if coins:

            prepare_shot()

        else:

            print()
            print("==============================")
            print("🎉 ALL COINS POCKETED!")
            print("==============================")

            waiting_for_next_shot = False

    # ------------------------------------------------
    # Move striker
    # ------------------------------------------------

    if shooting and selected_shot:

        hit_point = selected_shot["hit_point"]

        dx = hit_point[0] - striker[0]
        dy = hit_point[1] - striker[1]

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        if distance > 5:

            striker[0] += (
                dx / distance
                * STRIKER_SPEED
            )

            striker[1] += (
                dy / distance
                * STRIKER_SPEED
            )

        else:

            striker[0] = hit_point[0]
            striker[1] = hit_point[1]

            shooting = False
            coin_moving = True

            direction = selected_shot["direction"]

            coin_velocities[
                active_coin_index
            ][0] = direction[0] * SHOT_POWER

            coin_velocities[
                active_coin_index
            ][1] = direction[1] * SHOT_POWER

            print("STRIKER HIT COIN!")

    # ------------------------------------------------
    # Move coins
    # ------------------------------------------------

    if coin_moving:

        for i in range(len(coins)):

            coin = coins[i]
            velocity = coin_velocities[i]

            coin[0] += velocity[0]
            coin[1] += velocity[1]

            # ----------------------------------------
            # Cushions
            # ----------------------------------------

            if coin[0] - COIN_RADIUS <= LEFT:

                coin[0] = LEFT + COIN_RADIUS
                velocity[0] = abs(velocity[0]) * BOUNCE

            if coin[0] + COIN_RADIUS >= RIGHT:

                coin[0] = RIGHT - COIN_RADIUS
                velocity[0] = -abs(velocity[0]) * BOUNCE

            if coin[1] - COIN_RADIUS <= TOP:

                coin[1] = TOP + COIN_RADIUS
                velocity[1] = abs(velocity[1]) * BOUNCE

            if coin[1] + COIN_RADIUS >= BOTTOM:

                coin[1] = BOTTOM - COIN_RADIUS
                velocity[1] = -abs(velocity[1]) * BOUNCE

        # --------------------------------------------
        # Coin collisions
        # --------------------------------------------

        handle_coin_collisions()

        # --------------------------------------------
        # Pocket detection
        # --------------------------------------------

        check_pockets()

        # --------------------------------------------
        # Friction
        # --------------------------------------------

        for velocity in coin_velocities:

            velocity[0] *= FRICTION
            velocity[1] *= FRICTION

        # --------------------------------------------
        # Check movement
        # --------------------------------------------

        total_speed = 0

        for velocity in coin_velocities:

            total_speed += math.sqrt(
                velocity[0] ** 2
                + velocity[1] ** 2
            )

        if total_speed < STOP_SPEED:

            for velocity in coin_velocities:

                velocity[0] = 0.0
                velocity[1] = 0.0

            coin_moving = False
            shooting = False

            selected_shot = None
            active_coin_index = None

            waiting_for_next_shot = True

    # ------------------------------------------------
    # Draw
    # ------------------------------------------------

    screen.fill(DARK_WOOD)

    pygame.draw.rect(
        screen,
        WOOD,
        (
            LEFT,
            TOP,
            RIGHT - LEFT,
            BOTTOM - TOP
        )
    )

    # Pockets
    for pocket in pockets:

        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(pocket[0]),
                int(pocket[1])
            ),
            28
        )

    # ------------------------------------------------
    # AI path
    # ------------------------------------------------

    if selected_shot:

        target_coin = selected_shot["target_coin"]
        target_pocket = selected_shot["target_pocket"]
        hit_point = selected_shot["hit_point"]

        # Striker -> hit point

        pygame.draw.line(
            screen,
            RED,
            (
                int(striker[0]),
                int(striker[1])
            ),
            (
                int(hit_point[0]),
                int(hit_point[1])
            ),
            3
        )

        # Coin -> target

        if selected_shot["type"] == "DIRECT":

            pygame.draw.line(
                screen,
                GREEN,
                (
                    int(target_coin[0]),
                    int(target_coin[1])
                ),
                (
                    int(target_pocket[0]),
                    int(target_pocket[1])
                ),
                3
            )

        else:

            bounce = selected_shot["bounce"]

            pygame.draw.line(
                screen,
                GREEN,
                (
                    int(target_coin[0]),
                    int(target_coin[1])
                ),
                (
                    int(bounce[0]),
                    int(bounce[1])
                ),
                3
            )

            pygame.draw.line(
                screen,
                GREEN,
                (
                    int(bounce[0]),
                    int(bounce[1])
                ),
                (
                    int(target_pocket[0]),
                    int(target_pocket[1])
                ),
                3
            )

            pygame.draw.circle(
                screen,
                YELLOW,
                (
                    int(bounce[0]),
                    int(bounce[1])
                ),
                8
            )

    # ------------------------------------------------
    # Coins
    # ------------------------------------------------

    for i, coin in enumerate(coins):

        if (
            selected_shot
            and i == active_coin_index
        ):

            pygame.draw.circle(
                screen,
                YELLOW,
                (
                    int(coin[0]),
                    int(coin[1])
                ),
                COIN_RADIUS + 5
            )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(coin[0]),
                int(coin[1])
            ),
            COIN_RADIUS
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(coin[0]),
                int(coin[1])
            ),
            COIN_RADIUS,
            2
        )

    # ------------------------------------------------
    # Striker
    # ------------------------------------------------

    pygame.draw.circle(
        screen,
        BLUE,
        (
            int(striker[0]),
            int(striker[1])
        ),
        STRIKER_RADIUS
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (
            int(striker[0]),
            int(striker[1])
        ),
        STRIKER_RADIUS,
        2
    )

    pygame.display.flip()

    pygame.image.save(
        screen,
        "board.png"
    )

    clock.tick(60)


pygame.quit()
sys.exit()  