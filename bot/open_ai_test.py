import os
import time
import openai

from openai import OpenAI
from credentials import TOKEN_SEAFOOD_GURU

TOKEN = TOKEN_SEAFOOD_GURU
openai.api_key = os.environ['OPENAI_API_KEY']
assistant_id = 'asst_Ti4C9k9Dw2Se3j9zxjqWGAoY'

# assistant = openai.beta.assistants.retrieve(assistant_id=assistant_id)


class ChatGPTAssistant:
    def __init__(self, client, assistant_id):
        self.client = client
        self.thread_id = self.create_thread()
        self.assistant_id = assistant_id

    def create_thread(self):
        thread = openai.beta.threads.create()
        return thread.id

    # def get_assistant(self, assistant_id):
    #     assistant = openai.beta.assistants.retrieve(assistant_id)

    def send_message(self, content):
        # Send a message to a thread and return the message object
        message = openai.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=content
        )
        return message

    def display_messages(self):
        # Displaying responses
        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)

        for message in reversed(messages.data[:2]):
            print(message.role + ": " + message.content[0].text.value)

    def return_response(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
        print()
        response = reversed(messages.data[1])
        return response

    def run_assistant(self):
        # Check if a thread exists; if not, create a new one
        if not self.thread_id:
            self.thread_id = self.create_thread()

        print(self.thread_id)
        # Run the assistant and display responses
        run = self.client.beta.threads.runs.create(thread_id=self.thread_id, assistant_id=self.assistant_id)

        # Check the status of the run until it's completed
        while True:
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run.id)
            if run.status == 'completed':
                break
            # Wait for some time before checking again
            time.sleep(2)

        # Display responses
        # return self.display_messages()
        response =  self.return_response()
        print(response)
        return response

# client = OpenAI()
# a = ChatGPTAssistant(client, assistant_id)
# a.send_message('--> 1. Посоветуй мне как выбрать рыбы для сашими')
# a.run_assistant()
# a.send_message('--> 2. Подойдет ли для этого лосось?')
# a.run_assistant()
# a.send_message('--> 3. Как еще можно его приготовить?')
# a.run_assistant()
# a.send_message('--> 4. Что насчет варки супа?')
# a.run_assistant()

# print(openai.beta.threads.messages.list(thread_id="thread_QhOM7o73LeNNR6yCs3F4O0HE"))

messages = openai.beta.threads.messages.list(thread_id="thread_QhOM7o73LeNNR6yCs3F4O0HE")
print(next(reversed(messages.data[:1])).content[0].text.value)
# for message in reversed(messages.data[:1]):
#     print(message.role + ": " + message.content[0].text.value)


openai.beta.threads.messages.retrieve()
run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

