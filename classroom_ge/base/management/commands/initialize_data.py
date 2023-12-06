from django.core.management.base import BaseCommand
from base.models import Subject, Topic, MultipleChoiceQuestion, MultipleChoiceQuestionToTopics
from app_teacher.models import Level
from classroom_ge.settings import BASE_DIR
import json
import os
import re

class Command(BaseCommand):
    help = 'Initialize data in the database'
    
    def create_subjects(self):
        try:
            self.subject = Subject.objects.create(name_ka='მათემატიკა', name='მათემატიკა')
        except Exception as e:
            print(f'Error creating subject: {e}')
            print('Subject Math Already Exists')


    def create_class_levels(self):
        for level in range(1,13):
            try:
                Level.objects.create(level=level)
            except Exception as e:
                print(f'Error creating level: {e}')
                print(f'Level {level} already exists')


    def create_topics(self):
        dir_data_file = os.path.join(BASE_DIR, 'data', 'topics.json')
        
        myfile = open(dir_data_file, encoding="utf8")
        file_contents = json.load(myfile)

        for cur_entry in file_contents:
            try:
                Topic.objects.create(
                    identifier=cur_entry['topic'],
                    name=cur_entry['title_ka'],
                    name_ka=cur_entry['title_ka'],
                )
            except Exception as e:
                print(f'Error creating topic: {e}')
                print(f'Topic {cur_entry} already exists')


    def create_questions(self): # NOSONAR
        dir_data_file = os.path.join(BASE_DIR, 'data', 'problem_database.json')
        myfile = open(dir_data_file, encoding="utf8")
        file_contents = json.load(myfile)

        texts = file_contents['texts']
        choices_a = file_contents['a']
        choices_b = file_contents['b']
        choices_c = file_contents['c']
        choices_d = file_contents['d']
        answers = file_contents['ans']
        topics = file_contents['topics']

        assert len(texts) == len(choices_a) == len(choices_b) == len(choices_c) == len(choices_d) == len(answers) ==  len(topics)
        assert texts.keys() == choices_a.keys() == choices_b.keys() == choices_c.keys() == choices_d.keys() == answers.keys() == topics.keys()
        
        question_ids = texts.keys()

        for current_question_id in question_ids:
            cur_text = texts[current_question_id]
            cur_choice_a = choices_a[current_question_id]
            cur_choice_b = choices_b[current_question_id]
            cur_choice_c = choices_c[current_question_id]
            cur_choice_d = choices_d[current_question_id]
            cur_answer = answers[current_question_id]
            cur_topics = re.split(r',\s*|\s+', topics[current_question_id])
            
            choices = {
                "0": "{}",
                "1": "{}",
                "2": "{}",
                "3": "{}",
            }

            # Assuming cur_choice_a, cur_choice_b, cur_choice_c, cur_choice_d are variables with string values
            for i, cur_choice in enumerate([cur_choice_a, cur_choice_b, cur_choice_c, cur_choice_d]):
                if cur_choice is not None:  # Check if the value is not None
                    choices[str(i)] = cur_choice

            choices_string = ', '.join(f'"{k}": "{v}"' for k, v in choices.items())
            choices_string = '{' + choices_string + '}'

            cur_answer_int = ord(cur_answer) - ord('ა')
            
            try:
                cur_question = MultipleChoiceQuestion.objects.create(
                    id=current_question_id,
                    text=cur_text,
                    n_choices=4,
                    choices=choices_string,
                    correct_answer=cur_answer_int
                )
            except Exception as e:
                print(f'Error creating question: {e}')
                cur_question = MultipleChoiceQuestion.objects.get(
                    text=cur_text
                )
            

            if cur_question is not None:
                try:
                    for topic in cur_topics:
                        topic_from_topics_list = Topic.objects.get(identifier=topic)

                        if topic_from_topics_list == None:
                            print(f'Topic {topic} was not found in database')
                        else:
                            MultipleChoiceQuestionToTopics.objects.create(
                                topic=topic_from_topics_list,
                                question=cur_question
                            )
                except Exception as e:
                    print(f'Error creating MultipleChoiceQuestionToTopics object : {e}')
        


    def handle(self, *args, **options):
        # Add Subject
        # self.create_subjects()
        # self.create_topics()
        self.create_questions()

        # self.create_class_levels()

        

        