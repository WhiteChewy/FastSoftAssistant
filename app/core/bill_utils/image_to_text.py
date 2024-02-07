import os
import pathlib
import re
from typing import List, Tuple, Dict

import easyocr
from dotenv import load_dotenv


load_dotenv()
BILL_DIR = os.getenv('BILLS_DIR')
STRING_TYPES = os.getenv('STRING_TYPES')

reader = easyocr.Reader(['ru'])


def define_string_semantic(line: str) -> str:
    """Classify line as 'dish', 'number' or 'cost'

    In this function we classify given line by it semantic.

    :param line: line to classify
    :type line: str

    :return: string type
    :rtype: str
    """
    line = line.lower()
    number_re = re.compile("\d* *шт[.:;',-]*")
    cost_re = re.compile("\d+ *₽")
    if re.findall(number_re, line):
        return 'number'
    elif re.findall(cost_re, line):
        return 'cost'
    else:
        return 'dish'


def filter_only_dishes(raw_text: List[str]):
    """Get splited names of one dish and concatinate them

    :param raw_text: list of all lines from bill
    :type raw_text: List[str]

    :return: List of dishes from raw_text
    :rtype: tuple
    """
    dishes = []
    result = ''
    for elem in raw_text:
        if define_string_semantic(elem) == 'dish':
            result = result + ' ' + elem
        else:
            to_add = result if result != '' else None
            if to_add:
                dishes.append(result[1:])
                result = ''
    return dishes


def filter_numbers(numbers: List[str]) -> List[str]:
    """Get number of positions from list of parsed text.

    :param numbers: List of parsed numbers of positions
    :type numbers: List[str]

    :return: List of integers type numbers
    :rtype: List[str]
    """
    result = []

    for elem in numbers:
        index = elem.lower().find('шт')
        number = elem[:index]
        if not number:
            number = '1'
        result.append(int(number))
    
    return result


def filter_cost(numbers: List[str]) -> List[int]:
    """Get integers cost from string.

    :param numbers: List of strings wich contains cost of dishes
    :type numbers: List[str]

    :return: list of integers costs
    :rtype: List[int]
    """
    result = []

    for elem in numbers:
        index = elem.lower().find(' ₽')
        number = elem[:index].replace(' ', '')
        result.append(int(number))
    
    return result


def get_text_from_image(image_path: pathlib.Path) -> List[str]:
    """Get list of lines from image using easyocr.

    :param image_path: path to image
    :type image_path: pathlib.Path

    :return: List of lines from image
    :rtype: List[str]
    """
    extract_text = reader.readtext(str(image_path))
    lines = [line for _, line, _ in extract_text]
    begining_of_bill_index = lines.index('Мой счёт')
    filtered_lines = lines[begining_of_bill_index+1:]
    begin = 0
    for index, elem in enumerate(filtered_lines):
        if elem.split()[0].isdigit():
            continue
        else:
            begin = index + 2
            break
    if begin:
        filtered_lines = filtered_lines[begin:]
            
    return filtered_lines


def get_text_from_bill(image_dir: str=None, number_of_images: int=None) -> Dict[str, int]:
    """Get list of tuples contains (dish, number_of_dishes, total_cost).

    :param image_path: Path to bill images dir
    :type image_path: str

    :param number_of_images: How much images in dir
    :type number_of_images: int

    :return: Tuple of dishes withut number and total cost
    :rtype: dict
    """
    raw_text = []
    
    for elem in range(number_of_images):
        text = get_text_from_image(pathlib.Path(f'{BILL_DIR}/{elem}.jpg'))
        raw_text+=text
    only_dishes = filter_only_dishes(raw_text)
    only_cost = []
    only_numbers = []
    for elem in raw_text:
        line_class = define_string_semantic(elem)
        if line_class == 'cost':
            only_cost.append(elem)
        elif line_class == 'number':
            only_numbers.append(elem)
    
    only_numbers = filter_numbers(only_numbers)
    only_cost = filter_cost(only_cost)
    result = {dish: cost/number for dish, cost, number in zip(only_dishes, only_cost, only_numbers)}
    result.pop('Скидка', '')
    result.pop('Итого', '')
    result.pop('Всего', '')
    result.pop('Ошибка в чеке', '')
    return result
