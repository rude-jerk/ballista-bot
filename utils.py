import sqlite3
from collections import namedtuple
from time import time

BallistaNotification = namedtuple('BallistaNotification',
                                  ['recruitment_post', 'reminder'])


def notification_factory(cursor, row):
    return BallistaNotification(*row)


def get_ballista_entry(connection: sqlite3.Connection, match: dict) -> BallistaNotification:
    cursor = None
    notification = None
    try:
        cursor = connection.cursor()
        cursor.row_factory = notification_factory
        cursor.execute(
            '''
            SELECT recruitment_post, reminder FROM ballista_report
                WHERE entry_start = ?
                AND entry_end = ?
                AND actual_start = ?
                AND actual_end = ?;
            ''', (match['entryStart'],
                  match['entryEnd'],
                  match['start'],
                  match['end'])
        )
        notification = cursor.fetchone()
        if not notification:
            cursor.execute(
                '''
                INSERT INTO ballista_report VALUES (?, ?, ?, ?, 0, 0)
                ''', (match['entryStart'],
                      match['entryEnd'],
                      match['start'],
                      match['end'])
            )
            notification = BallistaNotification(0, 0)
    finally:
        if cursor:
            connection.commit()
            cursor.close()

    return notification


def update_ballista_entry(connection: sqlite3.Connection, match: dict, notification: BallistaNotification) -> bool:
    cursor = None
    success = False
    try:
        cursor = connection.cursor()
        cursor.execute(
            '''
            UPDATE ballista_report SET recruitment_post = ?, reminder = ?
                WHERE entry_start = ?
                AND entry_end = ?
                AND actual_start = ?
                AND actual_end = ?
            ''', (notification.recruitment_post,
                  notification.reminder,
                  match['entryStart'],
                  match['entryEnd'],
                  match['start'],
                  match['end'])
        )
        if cursor.rowcount > 0:
            success = True
    finally:
        if cursor:
            connection.commit()
            cursor.close()

    return success


def get_old_messages(connection: sqlite3.Connection) -> list:
    cursor = None
    messages = []
    cutoff_time = int(time() + 3600)
    try:
        cursor = connection.cursor()
        cursor.row_factory = notification_factory
        cursor.execute(
            '''
            SELECT recruitment_post, reminder FROM ballista_report WHERE actual_end BETWEEN 1 AND ? 
            AND (reminder > 0 OR recruitment_post > 0)
            ''', (cutoff_time,)
        )
        messages = cursor.fetchall()
        cursor.execute(
            '''
            UPDATE ballista_report SET reminder = -1, recruitment_post = -1 WHERE actual_end BETWEEN 1 AND ? 
            AND (reminder > 0 OR recruitment_post > 0)
            ''', (cutoff_time,)
        )
    finally:
        if cursor:
            connection.commit()
            cursor.close()

    return messages


def log_reset_request(connection: sqlite3.Connection, discord_user: str, account_user: str, char_name: str, email: str,
                      submitted: bool):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            '''
            INSERT INTO reset_log (discord_user, request_time, user_name, character_name, email_address, submitted) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (discord_user, time(), account_user, char_name, email, 'Y' if submitted else 'N')
        )
    finally:
        if cursor:
            connection.commit()
            cursor.close()
