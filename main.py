from PIL import Image, ImageDraw, ImageFilter
import random
import math
from classes.colors import Color

NB_STRING = 300
CANVAS_SIZE = 250
POP_SIZE = 100
NB_GENERATION = 100
STRING_WIDTH = 1

class Individu(object):
    def __init__(self, lines=None):
        if lines is not None:
            assert len(lines) == NB_STRING
            self.lines = lines
            return
        self.lines = []
        for _ in range(NB_STRING):
            angle1 = random.random()*math.pi*2
            x1 = (math.cos(angle1)*CANVAS_SIZE//2) + CANVAS_SIZE//2
            y1 = (math.sin(angle1)*CANVAS_SIZE//2) + CANVAS_SIZE//2
            angle2 = random.random()*math.pi*2
            x2 = (math.cos(angle2)*CANVAS_SIZE//2) + CANVAS_SIZE//2
            y2 = (math.sin(angle2)*CANVAS_SIZE//2) + CANVAS_SIZE//2
            self.lines.append((x1, y1, x2, y2))


def imageToCanvas(image):
    image = maskCircleSolid(image)
    imagePix = image.load()
    imageCanvas = [[imagePix[x,y] for x in range(CANVAS_SIZE)] for y in range(CANVAS_SIZE)]
    return imageCanvas

def createImageFromIndividu(individu):
    img = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255))
    img = maskCircleSolid(img)
    draw = ImageDraw.Draw(img)
    for x1,y1,x2,y2 in individu.lines:
        draw.line([(x1 , y1) ,(x2 , y2)], fill="black", width=STRING_WIDTH)
    return img

def saveDoubleCanvas(canvas1, canvas2, filename):
    res = []
    for r in canvas1:
        res.extend(map(tuple, r))
    im1 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE))
    im1.putdata(res)

    res = []
    for r in canvas2:
        res.extend(map(tuple, r))
    im2 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE))
    im2.putdata(res)

    im = Image.new('RGB', (CANVAS_SIZE * 2, CANVAS_SIZE))
    im.paste(im1, (0,0))
    im.paste(im2, (CANVAS_SIZE, 0))
    im.save(filename)


def maskCircleSolid(image):
    background = Image.new(image.mode, image.size, (0, 0, 0))
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)
    return Image.composite(image, background, mask)

def calcFitness(individu, final):
    ImageIndividu = createImageFromIndividu(individu)
    canvasIndividu = imageToCanvas(ImageIndividu)
    fit = 0;
    for x in range(CANVAS_SIZE):
        for y in range(CANVAS_SIZE):
            for c in range(3):
                fit += (canvasIndividu[x][y][c] - final[x][y][c]) ** 2
    return fit

def reproductionIndiv(indivg, indivd):
    poidsGauche = random.randrange(NB_STRING)
    enfant = indivg.lines[:poidsGauche] + indivd.lines[poidsGauche:]
    return Individu(enfant)

if __name__ == "__main__":
    image = Image.open('image.jpg').convert('L').convert('RGB').resize((CANVAS_SIZE, CANVAS_SIZE))
    imageCanvas = imageToCanvas(image)

    population = []
    for _ in range(POP_SIZE):
        population.append(Individu())

    for generation in range(NB_GENERATION):
        print('GENERATION', Color.PURPLE,generation, Color.END)
        popFitness = []
        for individu in population:
            popFitness.append((calcFitness(individu, imageCanvas), random.random(), individu))
        popFitness.sort()
        popFitness = popFitness[:POP_SIZE // 2]
        bestIndiv = min(zip(popFitness, population))[1]
        ImageIndividu = createImageFromIndividu(individu)
        canvasIndividu = imageToCanvas(ImageIndividu)
        saveDoubleCanvas(imageCanvas, canvasIndividu, f'results/generation{generation}.png')

        population = [popf[2] for popf in popFitness]
        enfants = []

        while len(enfants) + len(population) < POP_SIZE:
            parent1, parent2 = random.sample(population, 2)
            enfant = reproductionIndiv(parent1, parent2)
            enfants.append(enfant)
            
        population.extend(enfants)