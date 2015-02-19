import random as rand

WHITE = list(range(1, 60))
RED = list(range(1, 36))

def drawWhite():
    """
    """

    # Sample the white balls five times, without replacement.
    return rand.sample(WHITE, 5)

def drawRed():
    """
    """

    # Sample the red balls once.
    return RED[rand.randint(0, 34)]

def drawPowerball():
    """
    """

    # Draw the white balls and red ball.
    draw = drawWhite()
    draw.append(drawRed())

    return draw

def simJackpot():
    """
    """

    # Create the players numbers.
    playerWhite = set(drawWhite())
    playerRed = drawRed()

    # Initialize the intersection function (for speed).
    playerWhiteIntersection = playerWhite.intersection

    # Iterate until a jackpot is seen.
    run = True
    index = 0
    while run:
        # Create the winning numbers.
        winWhite = drawWhite()
        winRed = drawRed()

        # Check if the white ball numbers match.
        if playerWhiteIntersection(winWhite) == playerWhite:
            # If the red ball number matches, this is a jackpot.
            if playerRed == winRed:
                print("Jackpot!")
                run = False
            # If the red ball does not match, this is an almost jackpot.
            else:
                print("Almost Jackpot!")

        # Increment the index.
        index += 1

    return index, playerWhite, playerRed
