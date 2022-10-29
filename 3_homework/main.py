import csv
import os
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import NewType

import httpx
from loguru import logger
from returns.io import IO

Email = NewType('Email', str)


@dataclass
class User(object):

    id: int
    email: str


def valid_email(email: str) -> Email:
    if '@' not in email:
        raise ValueError
    return email


def emails_from_csv() -> list[Email]:
    with open('input.csv', 'r') as csv_file:
        emails = next(csv.reader(csv_file))
    res = []
    for email in emails:
        try:
            validated_email = valid_email(email[1:-1])
        except ValueError:
            logger.error(f'Email "{email}" invalid')
            continue
        res.append(validated_email)
    logger.info(f'Found {len(res)} users for parsing')
    return res


def users(emails: list[Email]) -> list[User]:
    with httpx.Client() as client:
        users = client.get('https://jsonplaceholder.typicode.com/users/').json()
    res = []
    for user in users:
        if user['email'] in emails:
            res.append(User(
                user['id'],
                user['email'],
            ))
    return res



def parse_part(user_id: int, part_name: str):
    start_time = time()
    with httpx.Client() as client:
        with open(f'users/{user_id}/{part_name}.json', 'w') as posts_file:
            posts_file.write(
                client.get(f'https://jsonplaceholder.typicode.com/users/{user_id}/{part_name}').text,
            )
    logger.info(f'User <{user_id}> {part_name} parsed. Time: {time() - start_time}')


def parse_user_data(users: list[User]):
    with suppress(FileExistsError):
        os.mkdir('users')
    for user in users:
        with suppress(FileExistsError):
            os.mkdir(f'users/{user.id}')
        logger.info('Start parsing user with email "{user.email}"')
        parse_part(user.id, 'posts')
        parse_part(user.id, 'albums')
        parse_part(user.id, 'todos')


if __name__ == '__main__':
    print(
        parse_user_data(
            users(
                emails_from_csv(),
            )
        )
    )

