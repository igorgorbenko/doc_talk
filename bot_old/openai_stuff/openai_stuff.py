import os
import time
from openai import OpenAI


class OpenAIAssistant:
    def __init__(self, openai_api_key, assistant_id):
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant_id = assistant_id

    def create_thread_and_run(self, user_input):
        # Create a thread for conversation
        thread = self.client.beta.threads.create()
        # Submit the initial message and start a run
        run = self.submit_message(thread.id, user_input)
        return thread, run

    def submit_message(self, thread_id, user_message):
        # Create a message in the thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )
        # Start a run after submitting the message
        return self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

    def get_response(self, thread_id):
        # Retrieve messages from the thread
        return self.client.beta.threads.messages.list(thread_id=thread_id, order="asc")

    def wait_on_run(self, run, thread_id):
        # Poll the run status until it is completed
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def fetch_formatted_response(self, user_input, thread_id=None):
        # Create thread, submit message, and fetch response
        if not thread_id:
            thread, run = self.create_thread_and_run(user_input)
            thread_id = thread.id
        else:
            run = self.submit_message(thread_id, user_input)

        self.wait_on_run(run, thread_id)
        messages = self.get_response(thread_id)
        return self.format_response(messages), thread_id

    def pretty_print(self, messages):
        # Print messages in a formatted way
        print("# Messages")
        for m in messages:
            print(f"{m.role}: {m.content[0].text.value}")
        print()

    # def format_response(self, messages):
    #     # Format the response text from the messages
    #     response_texts = []
    #     for message in messages.data:
    #         if message.role == 'assistant':
    #             response_texts.append(message.content[0].text.value)
    #     return " ".join(response_texts)

    def format_response(self, messages):
        # Adjust this method to return only the last assistant's response
        last_response = ""
        for message in messages.data:
            if message.role == 'assistant':
                last_response = message.content[0].text.value
        return last_response


# Usage
if __name__ == "__main__":
    assistant = OpenAIAssistant("asst_Ti4C9k9Dw2Se3j9zxjqWGAoY")
    response_text = assistant.fetch_formatted_response("Реши математическую задачку")
    print(response_text)
