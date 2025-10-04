from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def send_message(message, previous_response_id=None):
    message_lower = message.lower()

    if message_lower == 'quit':
        print("Koniec rozmowy.")
        exit()

    if message_lower == 'reset':
        print("Kontekst rozmowy został zresetowany.")
        return None

    if previous_response_id:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=message,
            previous_response_id=previous_response_id
        )
    else:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=message
        )

    print("AI:", response.output_text)
    return response.id

print('Zadawaj pytania, aby wyjść wpisz "quit". Aby zresetować kontekst wpisz "reset".')

prev_id = None

while True:
    user_input = input('Ty: ')
    prev_id = send_message(user_input, prev_id)