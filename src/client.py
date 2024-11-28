"""
    Client Program v5.0 Color Selection and Data Validation
    @author Teddy FitzPatrick
"""

import sys
import time

from datetime import datetime
from firebase import firebase
import pygame
import pygame_textinput

pygame.init()
pygame.font.init()

# Font
font = pygame.font.SysFont('Arial', 60)
small_font = pygame.font.SysFont('Arial', 12)
sorta_small_font = pygame.font.SysFont('Arial', 32)

# Set the window height to 3/5th of the screen height
info = pygame.display.Info()
WINDOW_WIDTH, WINDOW_HEIGHT = 0.5 * info.current_w, 0.6 * info.current_h
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Text Input and Box
text_input = pygame_textinput.TextInputVisualizer()
text_input.font_object = pygame.font.SysFont('Arial', 60)
text_input_box = pygame.rect.Rect(20, WINDOW_HEIGHT - 130, WINDOW_WIDTH - 60, 100)

# Message offset for scroll wheel
scroll_speed = 20
scroll_offset = 0

# Firebase reference
db_url = 'https://struglauk-default-rtdb.firebaseio.com/'
firebase = firebase.FirebaseApplication(db_url, None)

# Colors
WHITE, BLACK, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)
CUSTOM_ORANGE = (242, 139, 64)
CUSTOM_GREEN = (0, 128, 0)
CUSTOM_BLUE = (135, 206, 250)
TEAL = (0, 128, 128)

username = 'default_client'
# Default color selection
user_color = BLUE
received_color = CUSTOM_BLUE


def render_message(index: int, msg_packet: dict) -> None:
    global scroll_offset, received_color, user_color
    # Unpack message packet
    sent_by = msg_packet['username']
    message = msg_packet['message']
    timestamp = msg_packet['timestamp']

    # Calculate the vertical offset based off the message index
    vertical_offset = WINDOW_HEIGHT - 160 - index * 100 + scroll_offset

    # Create the message box
    msg_box = pygame.rect.Rect(20, vertical_offset - 90, WINDOW_WIDTH - 60, 80)
    pygame.draw.rect(window, user_color if sent_by == username else received_color, msg_box, 0, 15)

    # Render the message sender
    rendered_user = small_font.render(f'{sent_by}', True, WHITE)
    window.blit(rendered_user, (30, vertical_offset - 80))

    # Render the message content
    rendered_msg = font.render(f'{message}', False, WHITE)
    window.blit(rendered_msg, (30, vertical_offset - 80))

    # Render the timestamp
    formatted_timestamp = datetime.fromtimestamp(timestamp).strftime("%c")
    rendered_timestamp = small_font.render(f'{formatted_timestamp}', True, WHITE)
    window.blit(rendered_timestamp, (WINDOW_WIDTH - 225, vertical_offset - 80))


def main():
    global username, window, WINDOW_WIDTH, WINDOW_HEIGHT, text_input_box, scroll_offset
    # Initialize
    print('Client Started!')
    # Buffer of messages read in
    read_messages = []
    # Displayed messages
    message_queue = []
    # Primary message send/receive loop
    client_message = None
    while client_message != 'close_chat':
        # Send messages
        if client_message is not None:
            # Send the message
            post_message = {'username': username, 'message': client_message, 'timestamp': time.time()}
            try:
                firebase.post('/messages', post_message)
            except Exception as e:
                print('failed to send')
                print(f'message: {post_message['message']}')
                print(e.args)
            client_message = None
        # Get the messages dict
        messages: dict = firebase.get(db_url, 'messages')
        # Process messages
        if messages is not None:
            for msg_id, msg_packet in messages.items():
                # Delete old messages (20 minutes)
                # if time.time() - msg_packet['timestamp'] >= 1200:
                #     firebase.delete('messages', msg_id)
                # Ignore already read messages
                if msg_id in read_messages:
                    continue
                # Add message to the display queue
                message_queue.insert(0, msg_packet)
                # Mark message as read
                read_messages.append(msg_id)
        # GUI
        events = pygame.event.get()
        # Text Input Box
        text_input.update(events)
        # Event Handler
        for event in events:
            # Scrolling
            if event.type == pygame.MOUSEWHEEL:
                if event.y != 0:
                    # Apply a scrolling offset
                    scroll_offset += scroll_speed * event.y
                    # Limit scrolling too high above messages
                    if messages is not None and scroll_offset > len(messages) * 100 - WINDOW_HEIGHT + 240:
                            scroll_offset = len(messages) * 100 - WINDOW_HEIGHT + 240
                    # Limit scrolling below screen
                    if scroll_offset < 0:
                        scroll_offset = 0

            # Video Resize
            if event.type == pygame.VIDEORESIZE:
                # Everytime the window resizes, update the window WIDTH/HEIGHT variables
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                # Update the corresponding text input position
                text_input_box.update(20, WINDOW_HEIGHT - 130, WINDOW_WIDTH - 60, 100)
            # Typing
            if event.type == pygame.KEYDOWN:
                # Enter to terminate and send message
                if event.key == pygame.K_RETURN:
                    client_message = text_input.value
                    text_input.value = ''
            # Quit chat app
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # RENDERING
        window.fill(WHITE)  # White screen

        # Render messages
        for index, msg_packet in enumerate(message_queue):
            render_message(index, msg_packet)

        # Whiteout backdrop for text input box
        whiteout_rect = pygame.rect.Rect(0, WINDOW_HEIGHT - 150, WINDOW_WIDTH, 150)
        pygame.draw.rect(window, WHITE, whiteout_rect)

        # Render input text bar and border
        window.blit(text_input.surface, (30, WINDOW_HEIGHT - 110))  # Text In
        pygame.draw.rect(window, BLACK, text_input_box, 2, 15)  # Input Border Box

        # Update screen
        pygame.display.flip()
        # Wait 33 ms
        clock.tick(30)


def login() -> None:
    global username, received_color

    # Color selection
    # Received Message Colors
    received = sorta_small_font.render('Incoming Color: ', True, WHITE)

    CUSTOM_BLUE_SELECT = pygame.Rect(40, 100, 40, 40)
    TEAL_SELECT = pygame.Rect(100, 100, 40, 40)
    CUSTOM_ORANGE_SELECT = pygame.Rect(160, 100, 40, 40)
    CUSTOM_GREEN_SELECT = pygame.Rect(220, 100, 40, 40)

    selection_box = pygame.Rect(37, 97, 46, 46)

    # Title
    title = font.render('Enter a username:', True, WHITE)
    title_rect = title.get_rect()
    t_width, t_height = title_rect.width, title_rect.height
    # Text Back
    text_back = pygame.rect.Rect(WINDOW_WIDTH / 2 - t_width / 2, WINDOW_HEIGHT / 2, t_width, 100)
    # Text input
    username_input = pygame_textinput.TextInputVisualizer()
    username_input.font_object = pygame.font.SysFont('Arial', 60)
    username_request = None
    while True:
        # Event Handler
        events = pygame.event.get()
        username_input.update(events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Color selection mouse click
                if CUSTOM_BLUE_SELECT.collidepoint(pygame.mouse.get_pos()):
                    received_color = CUSTOM_BLUE
                    selection_box = pygame.Rect(37, 97, 46, 46)

                elif TEAL_SELECT.collidepoint(pygame.mouse.get_pos()):
                    received_color = TEAL
                    selection_box = pygame.Rect(97, 97, 46, 46)

                elif CUSTOM_ORANGE_SELECT.collidepoint(pygame.mouse.get_pos()):
                    received_color = CUSTOM_ORANGE
                    selection_box = pygame.Rect(157, 97, 46, 46)

                elif CUSTOM_GREEN_SELECT.collidepoint(pygame.mouse.get_pos()):
                    received_color = CUSTOM_GREEN
                    selection_box = pygame.Rect(217, 97, 46, 46)

            # Quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                # Submit username request
                if event.key == pygame.K_RETURN:
                    username_request = username_input.value
                    username_input.value = ''
        # Process username request
        if username_request is not None:
            # Username must be between length 2 and 10
            if 2 <= len(username_request) <= 10:
                username = username_request
                return
            username_request = None

        # RENDERING
        window.fill(BLACK)

        # Color boxes
        # Received Messages Color selector
        window.blit(received, (40, 40))

        pygame.draw.rect(window, RED, selection_box)
        pygame.draw.rect(window, CUSTOM_BLUE, CUSTOM_BLUE_SELECT)
        pygame.draw.rect(window, TEAL, TEAL_SELECT)
        pygame.draw.rect(window, CUSTOM_ORANGE, CUSTOM_ORANGE_SELECT)
        pygame.draw.rect(window, CUSTOM_GREEN, CUSTOM_GREEN_SELECT)

        # Text Back
        pygame.draw.rect(window, WHITE, text_back, 0, 15)
        # Text input
        window.blit(username_input.surface, (20 + WINDOW_WIDTH / 2 - t_width / 2, 20 + WINDOW_HEIGHT / 2))
        # Title
        window.blit(title, (WINDOW_WIDTH / 2 - t_width / 2, WINDOW_HEIGHT / 2 - 100))
        # Update screen
        pygame.display.flip()
        # Wait 33 ms
        clock.tick()


if __name__ == '__main__':
    # firebase.delete('/messages', '')
    login()
    pygame.display.set_caption(f'Python Chat App (Login: {username})')
    # Run app
    main()
