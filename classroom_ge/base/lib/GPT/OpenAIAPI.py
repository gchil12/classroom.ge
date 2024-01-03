#%%
#%%
import threading
import requests
import json
from app_student.models import StudentQuestion

api_key = "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"

# The API URL for GPT-3.5-turbo model
url = "https://api.openai.com/v1/chat/completions"

# Headers including the Authorization with your API key
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}


class OpenAIThread(threading.Thread):
    def __init__(self, prompts):
        self.prompts = prompts
        threading.Thread.__init__(self)

    def run(self):
        for prompt in self.prompts:
            try:
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                f"Question: {prompt['question_text']} Students Answer: {prompt['student_answer']}. "
                                f"Students Explanation: {prompt['student_explanation']}. "
                                "Evaluate the students answer and explanation by the following criteria: "
                                "Knowledge: How well does the student understand the concepts stated in the exercise? Evaluate from 0 to 10. "
                                "Reasoning: Does the student wrote clear explanation? Does the student follow proper logic to solve the problem? Evaluate from 0 to 10. "
                                "Formulation: How clearly and consistently does the student formulate the answer? Evaluate from 0 to 10. "
                                "Answer me only with numbers, without explanation."
                            )
                        }
                    ],
                    "temperature": 0.7
                }

                response = requests.post(url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0 and 'message' in response_data['choices'][0]:
                        # Extracting the content from the response
                        response_content = response_data['choices'][0]['message']['content']
                        
                        lines = response_content.split('\n')
                        results = {}

                        for line in lines:
                            # Splitting each line by colon
                            key, value = line.split(':')

                            # Stripping whitespace from key and converting value to integer
                            key = key.strip()
                            value = int(value.strip())

                            results[key] = value

                    prompt['question'].submitted_to_gpt = True
                    prompt['question'].gpt_knowledge = results['Knowledge']
                    prompt['question'].gpt_reasoning = results['Reasoning']
                    prompt['question'].gpt_formulation = results['Formulation']

                    prompt['question'].save()
                else:
                    print("Error:", response.status_code, response.text)
            
            except Exception as e:
                print(f'Error in OpenAI Integration {e}')