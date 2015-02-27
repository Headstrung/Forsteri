import random as rand

def createPerm(redCount, blueCount):
    """
    """

    # Create a list of the possibilities.
    comb = ["R"] * redCount + ["B"] * blueCount

    # Shuffle the possibilities.
    rand.shuffle(comb)

    return comb

def game(redCount, blueCount, drawCount):
    """
    """

    # Create a permutaion of the possibilities.
    perm = createPerm(redCount, blueCount)
    drawAll = []
    leftAll = [[redCount, blueCount]]

    for i in range(redCount + blueCount, 0, -drawCount):
        drawTurn = []
        for j in range(0, drawCount):
            try:
                select = rand.randrange(0, len(perm))
                drawTurn.append(perm.pop(select))
            except ValueError:
                pass
        drawAll.append(drawTurn)
        redDraw = sum([1 if i == "R" else 0 for i in drawTurn])
        blueDraw = len(drawTurn) - redDraw
        leftAll.append([leftAll[-1][0] - redDraw, leftAll[-1][1] - blueDraw])

    return drawAll, leftAll
