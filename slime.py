from cmath import cos, sin
import math
import numpy
import pygame
import random
from vector import Vector, random_vector
import vector

pygame.init()

font = pygame.font.Font("freesansbold.ttf", 15)


class ActiveCoord:
    def __init__(self, x: int, y: int):
        self.y = y
        self.x = x


class Agent:
    def __init__(
        self,
        position: Vector,
        newPos: Vector,
        angle: float,
        sensorV1: Vector,
        sensorV2: Vector,
        sensorV3: Vector,
        culture: float,
    ):
        self.position = position
        self.angle = angle
        self.newPos = newPos
        self.sensorV1 = sensorV1
        self.sensorV2 = sensorV2
        self.sensorV3 = sensorV3
        self.culture = culture


delta_time = 0.0
clock = pygame.time.Clock()


numOfAgents = 400
TMDiv = 10
screenSize = 1000
moveSpeed = 4.0
drawPheramone = False
trailLifeTime = 300
blueCulture = False
randomDegree = 0.01  # 100<


ArrayAgents = numpy.empty(numOfAgents, dtype=Agent)
ActiveCoordArray = [ActiveCoord(0, 0)]
agentStartingPosition = Vector(screenSize / 2, screenSize / 2)
agentStartingAngle = random.random() * 180
direction = Vector(math.cos(agentStartingAngle), math.sin(agentStartingAngle))


mousePositionVector = (0, 0)
numOfAgentsText = font.render(str(numOfAgents), 1, (255, 255, 255))
moveSpeedText = font.render(str(moveSpeed), 1, (255, 255, 255))
trailLifeTimeText = font.render(str(trailLifeTime / 100), 1, (255, 255, 255))
blueCultureText = font.render(str(blueCulture), 1, (150, 150, 255))

for n in range(numOfAgents):
    ArrayAgents[n] = Agent(
        agentStartingPosition,
        Vector(0, 0),
        agentStartingAngle,
        agentStartingPosition + direction * moveSpeed * delta_time,
        agentStartingPosition + direction * moveSpeed * delta_time,
        agentStartingPosition + direction * moveSpeed * delta_time,
        0,
    )
    agentStartingAngle = agentStartingAngle = random.random() * 180


screen = pygame.display.set_mode((screenSize, screenSize))


TMsectionAmount = screenSize / TMDiv
TrailMap = numpy.zeros((int(screenSize / TMDiv), int(screenSize / TMDiv)))
trailFollow = Vector(0, 0)

simRunning = True
agentStart = False
viewAgent = True
viewPheramone = True
showText = True

alphaTick = 1
alphaMaxTick = 5


backgroundAlpha = 5

backgroundPic = pygame.transform.scale(
    pygame.image.load("background.png").convert_alpha(), (screenSize, screenSize)
)
backgroundRect = backgroundPic.get_rect(center=(screenSize / 2, screenSize / 2))


def moveSensors(agentX: Agent):
    agentX.sensorV1 = (
        agentX.position
        # + Vector(math.cos(agentX.angle), math.sin(agentX.angle)) * moveSpeed
    )

    agentX.sensorV2 = (
        agentX.position
        + Vector(math.cos(agentX.angle + 0.5), math.sin(agentX.angle + 0.5))
        * moveSpeed
        * 20
    )
    agentX.sensorV3 = (
        agentX.position
        + Vector(math.cos(agentX.angle - 0.5), math.sin(agentX.angle - 0.5))
        * moveSpeed
        * 20
    )


def checkSensors(agentX: Agent):
    global randomDegree
    angleChange = 0.1
    angleDir = 0
    if (
        random.random() >= 0.01 * randomDegree
    ):  # checks if it will move randomly or according to sensor

        if (
            int(agentX.sensorV2.x / TMDiv) < TMsectionAmount
            and int(agentX.sensorV2.x / TMDiv) > 0
            and int(agentX.sensorV2.y / TMDiv) < TMsectionAmount
            and int(agentX.sensorV2.y / TMDiv) > 0
            # checks if sensor 2 is in bounds
        ):
            if (
                TrailMap[int(agentX.sensorV2.x / TMDiv)][int(agentX.sensorV2.y / TMDiv)]
                > 0.0
                # checks if the sensor is detecting a square greater than one ( white culture )
            ):
                if (
                    agentX.culture == 1
                ):  # if its greater than one and the agent is of the white culture
                    angleDir = angleChange  # turn towards
                if (
                    agentX.culture == -1
                ):  # if its greater than one and the agent is of the blue culture
                    angleDir = -angleChange  # turn away
            elif (
                TrailMap[int(agentX.sensorV2.x / TMDiv)][int(agentX.sensorV2.y / TMDiv)]
                < 0.0
                # checks if the sensor is detecting a square less than one ( blue culture )
            ):
                if (
                    agentX.culture == 1
                ):  # if its greater than one and the agent is of the white culture
                    angleDir = -angleChange  # turn away
                if (
                    agentX.culture == -1
                ):  # if its greater than one and the agent is of the blue culture
                    angleDir = angleChange  # turn towards

        if (
            int(agentX.sensorV3.x / TMDiv) < TMsectionAmount
            and int(agentX.sensorV3.x / TMDiv) > 0
            and int(agentX.sensorV3.y / TMDiv) < TMsectionAmount
            and int(agentX.sensorV3.y / TMDiv) > 0
            # checks if sensor 3 is in bounds
        ):
            if (
                TrailMap[int(agentX.sensorV3.x / TMDiv)][int(agentX.sensorV3.y / TMDiv)]
                > 0.0
                # checks if the sensor is detecting a square greater than one
            ):
                if (
                    agentX.culture == 1
                ):  # if its greater than one and the agent is of the white culture
                    angleDir = -angleChange  # turn towards
                if (
                    agentX.culture == -1
                ):  # if its greater than one and the agent is of the blue culture
                    angleDir = angleChange  # turn away
            elif (
                TrailMap[int(agentX.sensorV3.x / TMDiv)][int(agentX.sensorV3.y / TMDiv)]
                < 0.0
                # checks if the sensor is detecting a square less than one
            ):
                if (
                    agentX.culture == 1
                ):  # if its less than one and the agent is of the white culture
                    angleDir = angleChange  # turn away
                if (
                    agentX.culture == -1
                ):  # if its less than one and the agent is of the blue culture
                    angleDir = -angleChange  # turn towards

        if (
            int(agentX.sensorV2.x / TMDiv) < TMsectionAmount
            and int(agentX.sensorV2.x / TMDiv) > 0
            and int(agentX.sensorV2.y / TMDiv) < TMsectionAmount
            and int(agentX.sensorV2.y / TMDiv) > 0
            and int(agentX.sensorV3.x / TMDiv) < TMsectionAmount
            and int(agentX.sensorV3.x / TMDiv) > 0
            and int(agentX.sensorV3.y / TMDiv) < TMsectionAmount
            and int(agentX.sensorV3.y / TMDiv) > 0
            # checks if both sensors are in bounds
        ):
            if (
                TrailMap[int(agentX.sensorV2.x / TMDiv)][int(agentX.sensorV2.y / TMDiv)]
                > 0.0
                and TrailMap[int(agentX.sensorV3.x / TMDiv)][
                    int(agentX.sensorV3.y / TMDiv)
                ]
                > 0.0
                # if both sensors are detecting a square that is greater than one
            ):
                if (
                    TrailMap[int(agentX.sensorV2.x / TMDiv)][
                        int(agentX.sensorV2.y / TMDiv)
                    ]
                    > TrailMap[int(agentX.sensorV3.x / TMDiv)][
                        int(agentX.sensorV3.y / TMDiv)
                    ]
                    # if Sensor 2 is larger
                ):
                    if (
                        agentX.culture == 1
                    ):  # if its more than than one and the agent is of the white culture
                        angleDir = angleChange  # turn towards
                    if (
                        agentX.culture == -1
                    ):  # if its more than than one and the agent is of the blue culture
                        angleDir = -angleChange  # turn away
                if (
                    TrailMap[int(agentX.sensorV2.x / TMDiv)][
                        int(agentX.sensorV2.y / TMDiv)
                    ]
                    < TrailMap[int(agentX.sensorV3.x / TMDiv)][
                        int(agentX.sensorV3.y / TMDiv)
                    ]
                    # if Sensor 3 is larger
                ):
                    if (
                        agentX.culture == 1
                    ):  # if its less than than one and the agent is of the white culture
                        angleDir = -angleChange  # turn towards
                    if (
                        agentX.culture == -1
                    ):  # if its less than than one and the agent is of the blue culture
                        angleDir = angleChange  # turn away

            if (
                TrailMap[int(agentX.sensorV2.x / TMDiv)][int(agentX.sensorV2.y / TMDiv)]
                < 0.0
                and TrailMap[int(agentX.sensorV3.x / TMDiv)][
                    int(agentX.sensorV3.y / TMDiv)
                ]
                < 0.0
                # if both sensors are detecting a square that is less than than one
            ):
                if (
                    TrailMap[int(agentX.sensorV2.x / TMDiv)][
                        int(agentX.sensorV2.y / TMDiv)
                    ]
                    < TrailMap[int(agentX.sensorV3.x / TMDiv)][
                        int(agentX.sensorV3.y / TMDiv)
                    ]
                    # if Sensor 2 is smaller
                ):
                    if (
                        agentX.culture == 1
                    ):  # if its less than than one and the agent is of the white culture
                        angleDir = -angleChange  # turn away
                    if (
                        agentX.culture == -1
                    ):  # if its less than than one and the agent is of the blue culture
                        angleDir = angleChange  # turn towards
                if (
                    TrailMap[int(agentX.sensorV2.x / TMDiv)][
                        int(agentX.sensorV2.y / TMDiv)
                    ]
                    < TrailMap[int(agentX.sensorV3.x / TMDiv)][
                        int(agentX.sensorV3.y / TMDiv)
                    ]
                    # if Sensor 3 is smaller
                ):
                    if (
                        agentX.culture == 1
                    ):  # if its less than than one and the agent is of the white culture
                        angleDir = angleChange  # turn towards
                    if (
                        agentX.culture == -1
                    ):  # if its less than than one and the agent is of the blue culture
                        angleDir = -angleChange  # turn turn towards
        if (
            TrailMap[int(agentX.sensorV1.x / TMDiv)][int(agentX.sensorV1.y / TMDiv)]
            == -agentX.culture
        ):
            angleDir = angleChange
        agentX.angle += angleDir

    else:
        agentX.angle += random.random() / 2
        # turn randomly sometimes


def moveAgents():
    global ActiveCoordArray
    for agentX in ArrayAgents:
        if agentStart:

            direction = (
                Vector(math.cos(agentX.angle), math.sin(agentX.angle)) + trailFollow
            )

            if (agentX.position + direction * moveSpeed).x >= screenSize or (
                agentX.position + direction * moveSpeed
            ).x <= 0:
                agentX.angle = random.random() * 180
            elif (agentX.position + direction * moveSpeed).y >= screenSize or (
                agentX.position + direction * moveSpeed
            ).y <= 0:
                agentX.angle = random.random() * 180
            else:
                if (
                    not TrailMap[int(agentX.position.x / TMDiv)][
                        int(agentX.position.y / TMDiv)
                    ]
                    > 1
                ):
                    TrailMap[int(agentX.position.x / TMDiv)][
                        int(agentX.position.y / TMDiv)
                    ] = (1.0 * agentX.culture)

                # TODO: Optimize checking if coord is already active

                # addCoord = True
                # for n in ActiveCoordArray:
                #     if n.x == int(agentX.position.x / TMDiv) and n.y == int(
                #         agentX.position.y / TMDiv
                #     ):
                #         addCoord = False
                # if addCoord:
                #     ActiveCoordArray.append(
                #         ActiveCoord(
                #             int(agentX.position.x / TMDiv),
                #             int(agentX.position.y / TMDiv),
                #         )
                #     )

                # print(len(ActiveCoordArray))

                moveSensors(agentX)
                checkSensors(agentX)

                agentX.newPos = agentX.position + direction * moveSpeed

            agentX.position = agentX.newPos
        else:
            agentX.position = agentStartingPosition


def update():
    moveAgents()
    pass


def ProcessTrailMap():
    # global ActiveCoordArray
    if agentStart:
        for n in ArrayAgents:
            if n.culture == 1:
                pygame.draw.ellipse(
                    screen,
                    (255, 255, 255),
                    pygame.Rect(n.position.x - 2, n.position.y - 2, 4, 4),
                )
            elif n.culture == -1:
                pygame.draw.ellipse(
                    screen,
                    (105, 105, 115),
                    pygame.Rect(n.position.x - 2, n.position.y - 2, 4, 4),
                )
    # TODO: Make sure that coords are being removed from Active coord array
    # if viewAgent:
    #     for n in ActiveCoordArray:
    #         if TrailMap[n.x][n.y] > 0.0:
    #             if TrailMap[n.x][n.y] - 1 / trailLifeTime > 0:
    #                 TrailMap[n.x][n.y] = TrailMap[n.x][n.y] - 1 / trailLifeTime
    #             else:
    #                 TrailMap[n.x][n.y] = 0
    #                 ActiveCoordArray.remove(n)
    #                 print("remove")

    #         elif TrailMap[n.x][n.y] < 0.0:

    #             if TrailMap[n.x][n.y] + 1 / trailLifeTime < 0:
    #                 TrailMap[n.x][n.y] = TrailMap[n.x][n.y] + 1 / trailLifeTime
    #             else:
    #                 TrailMap[n.x][n.y] = 0
    #                 ActiveCoordArray.remove(n)
    #                 print("remove")

    for r in range(int(TrailMap.size / TMsectionAmount)):
        for c in range(TrailMap[r].size):
            if TrailMap[r][c] > 0.0:
                if viewAgent:
                    if TrailMap[r][c] - 1 / trailLifeTime > 0:
                        TrailMap[r][c] = TrailMap[r][c] - 1 / trailLifeTime
                    else:
                        TrailMap[r][c] = 0
            elif TrailMap[r][c] < 0 and TrailMap[r][c] < 1.1:
                if viewAgent:
                    if TrailMap[r][c] + 1 / trailLifeTime < 0:
                        TrailMap[r][c] = TrailMap[r][c] + 1 / trailLifeTime
                    else:
                        TrailMap[r][c] = 0


def drawPheramoneTrail():
    if drawPheramone:
        for offSetX in range(-2, 3):
            for offSetY in range(-2, 3):
                TrailMap[int(mousePositionVector[0] / TMDiv) + offSetX][
                    int(mousePositionVector[1] / TMDiv) + offSetY
                ] = 2


def draw():
    global alphaTick
    global alphaMaxTick

    if alphaTick == alphaMaxTick:
        backgroundPic.set_alpha(backgroundAlpha)
        screen.blit(backgroundPic, backgroundRect)
        alphaTick = 1
    else:
        alphaTick += 1

    if showText:
        numOfAgentsText = font.render(str(numOfAgents), 1, (150, 150, 255))
        screen.blit(
            font.render("Agents             [-  +]: ", 1, (255, 255, 255)), (10, 10)
        )
        screen.blit(numOfAgentsText, (190, 10))

        moveSpeedText = font.render(str(moveSpeed), 1, (150, 150, 255))
        screen.blit(
            font.render("Move Speed    [-1  +2]: ", 1, (255, 255, 255)), (10, 30)
        )
        screen.blit(moveSpeedText, (190, 30))

        trailLifeTimeText = font.render(str(trailLifeTime / 100), 1, (150, 150, 255))
        screen.blit(
            font.render("Trail Life Time [-3  +4]: ", 1, (255, 255, 255)), (10, 50)
        )
        screen.blit(trailLifeTimeText, (190, 50))

        blueCultureText = font.render(str(blueCulture), 1, (150, 150, 255))
        screen.blit(font.render("Blue Culture [G]: ", 1, (255, 255, 255)), (10, 70))
        screen.blit(blueCultureText, (190, 70))

        screen.blit(
            font.render("Toggle Showing Pheromone [P]", 1, (255, 255, 255)), (10, 90)
        )
        screen.blit(
            font.render("Toggle Showing Spores [V]", 1, (255, 255, 255)), (10, 110)
        )
        screen.blit(
            font.render("Toggle Showing Controls [C]", 1, (255, 255, 255)), (300, 10)
        )
        screen.blit(font.render("Blur [B](Beta)", 1, (255, 255, 255)), (300, 30))
        screen.blit(
            font.render("Click to place Pheromone", 1, (255, 255, 255)), (300, 50)
        )
        screen.blit(
            font.render(
                "Restart (click twice to remove pheromones [R])", 1, (255, 255, 255)
            ),
            (300, 70),
        )

    ProcessTrailMap()


while simRunning:
    mousePositionVector = pygame.mouse.get_pos()

    drawPheramoneTrail()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                simRunning = False
            if event.key == pygame.K_SPACE:
                agentStart = True
                ArrayAgents = numpy.empty(numOfAgents, dtype=Agent)
                for n in range(numOfAgents):
                    cultureChoose = 1
                    if random.random() > 0.5 and blueCulture:
                        cultureChoose = -1
                    else:
                        cultureChoose = 1
                    ArrayAgents[n] = Agent(
                        agentStartingPosition,
                        Vector(0, 0),
                        agentStartingAngle,
                        agentStartingPosition + direction * moveSpeed * delta_time,
                        agentStartingPosition + direction * moveSpeed * delta_time,
                        agentStartingPosition + direction * moveSpeed * delta_time,
                        cultureChoose,
                    )
                    agentStartingAngle = agentStartingAngle = random.random() * 180
            if event.key == pygame.K_v:
                viewAgent = not viewAgent
            if event.key == pygame.K_b:
                blur = not blur
            if event.key == pygame.K_p:
                viewPheramone = not viewPheramone
            if event.key == pygame.K_c:
                showText = not showText
            if event.key == pygame.K_EQUALS:
                if not agentStart:
                    numOfAgents += 10
            if event.key == pygame.K_MINUS:
                if not agentStart:
                    numOfAgents -= 10
            if event.key == pygame.K_2:
                if not agentStart:
                    moveSpeed += 0.2
            if event.key == pygame.K_1:
                if not agentStart:
                    moveSpeed -= 0.2
            if event.key == pygame.K_4:
                if not agentStart:
                    trailLifeTime += 20
            if event.key == pygame.K_3:
                if not agentStart:
                    trailLifeTime -= 20
            if event.key == pygame.K_g:
                blueCulture = not blueCulture
            if event.key == pygame.K_r:
                if agentStart:
                    agentStart = False
                    for n in range(numOfAgents):
                        ArrayAgents[n].position = agentStartingPosition
                    for r in range(int(TrailMap.size / TMsectionAmount)):
                        for c in range(TrailMap[r].size):
                            if TrailMap[r][c] < 2:
                                TrailMap[r][c] = 0
                else:
                    for r in range(int(TrailMap.size / TMsectionAmount)):
                        for c in range(TrailMap[r].size):
                            TrailMap[r][c] = 0
                    agentStartingPosition = Vector(screenSize / 2, screenSize / 2)
            if event.key == pygame.K_f:
                agentStartingPosition = Vector(
                    mousePositionVector[0], mousePositionVector[1]
                )
        if event.type == pygame.MOUSEBUTTONDOWN:
            drawPheramone = True
        if event.type == pygame.MOUSEBUTTONUP:
            drawPheramone = False

    update()
    draw()

    pygame.display.flip()

    delta_time = 0.001 * clock.tick(144)


pygame.quit()
quit()
