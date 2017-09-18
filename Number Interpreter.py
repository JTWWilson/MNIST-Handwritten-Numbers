import pygame
from math import *


def get_images(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    labels = []
    # Generate list of all the real numbers and handwritten scans
    images = []
    for line in lines:
        images.append([int(i) for i in line.split(',')])
        labels.append(int(line[0]))
    return images, labels


def sort_images(lines):
    """
    Sorts numbers into separate digits
    :param lines: List of images
    :return: Dictionary of sorted images
    """
    sorted_numbers = {'0' : [], '1' : [], '2' : [], '3' : [], '4' : [], '5' : [], '6' : [], '7' : [], '8' : [], '9' : []}
    for line in lines:
        if line[0] in sorted_numbers.keys():
            sorted_numbers[line[0]].append(line[1:])
    return sorted_numbers


def form_weighting(weighting, additions):
    """
    Forms a weighting from the old weighting and a list of additions
    :param weighting: The original weighting of the number
    :param additions: The images to be added to the weighting
    :return: The new weighting
    """
    assert len(additions) == 28 * 28
    if len(additions) == 0: return weighting
    if isinstance(additions, list):
        if not isinstance(additions[0], list):
            additions = [additions]
    lst = []
    for pixel in range(28 * 28):
        return sum([weighting[pixel + 2] * weighting[1], *[addition[pixel] for addition in additions]]) / (int(weighting[1]) + len(additions))
        #lst.append(str(sum(
        #    [float(image[pixel])
        #                    for image in [pix for pix in weighting, *addition(weighting[2:] * int(weighting[1]), *addition[1:])])
        #               / (float(weighting[1]) + len(addition))))

    return [weighting[0], int(weighting[1]) + 1, *lst]
    #return [str(sum([float(image[pixel]) for image in (weighting, *addition)]) / len(series)) for pixel in range(28 * 28)]


def compare_images(image1, image2):
    """
    Compares two images and returns the amount by which they are different
    :param image1: First image
    :param image2: Second image
    :return: Difference
    """
    assert len(image1) == 28 * 28, 'Image1 is not of length 784 but {}: {}'.format(len(image1), image1)
    assert len(image2) == 28 * 28, 'Image2 is not of length 784 but {}: {}'.format(len(image2), image2)
    return abs(sum([float(image1[pixel]) - float(image2[pixel]) for pixel in range(28 * 28)]))


def estimate_number(weightings, image):
    return sorted([(weighting[0], compare_images(weighting[2:], image)) for weighting in weightings], key=lambda probability: float(probability[1]))


def show_number(numbers):
    pygame.init()
    window = pygame.display.set_mode((280 * len(numbers), 280))
    for index, number in enumerate(numbers):
        for pixel_index, pixel in enumerate(number[-784:]):
            pygame.draw.rect(window, (floor(pixel), floor(pixel), floor(pixel)), (index * 280 + (pixel_index % 28) * 10, (pixel_index // 28) * 10, 10, 10))
    pygame.display.flip()
    input()
    pygame.quit()


if __name__ == '__main__':
    while True:
        image_path = input('Path to image: ')
        # image_path =  'mnist_test.csv'
        mode = input('Training (tr) or testing (te): ')
        images, labels = get_images(image_path)
        raw_weightings = open('weightings.csv', 'r+')
        weightings = [[float(j) for j in i.rstrip(',\n').split(',')] for i in raw_weightings.readlines()]
        assert len(weightings[1]) == 28 * 28 + 2, 'Image1 is not of length 786 but {}: {}'.format(len(weightings[1]), weightings[1])
        successes = 0
        for index, image in enumerate(images):
            assert len(weightings[1]) == 28 * 28 + 2, 'Image1 is not of length 786 but {}: {}'.format(len(weightings[1]), weightings[1])
            probabilities = estimate_number(weightings, image[1:])
            print('I think that number {0} is "{1}"\nThe real value is "{2}"\nProbabilities: {3}\n'.format(
                index + 1, probabilities[0][0], image[0], ', '.join([''.join(str(i)) for i in probabilities])))
            show_number([image, *[weightings[int(i[0])] for i in probabilities]])
            if image[0] == probabilities[0][0]:
                successes += 1
            if mode.lower() == 'tr':
                weightings[int(image[0])] = form_weighting(weightings[int(image[0])], image[1:])

        if mode.lower() == 'tr':
            raw_weightings.truncate()
            raw_weightings.close()
            open('weightings.csv', 'w').close()
            new_weightings = open('weightings.csv', 'w')
            for weighting in weightings:
                for i in weighting:
                    new_weightings.write(str(i) + ',')
                new_weightings.write('\n')
            new_weightings.close()
        print('Success rate: {}%'.format((successes / len(images)) * 100))
