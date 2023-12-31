from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Subquery, OuterRef
from base.models import Subject, Topic, Question, QuestionToTopic, QuestionChoice, VideoLecture, VideoToTopic, VideoToSubject
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
        subject_math = Subject.objects.all().first()

        dir_data_file = os.path.join(BASE_DIR, 'data', 'topics.json')
        
        myfile = open(dir_data_file, encoding="utf8")
        file_contents = json.load(myfile)

        for cur_entry in file_contents:
            try:
                Topic.objects.create(
                    identifier=cur_entry['topic'],
                    name=cur_entry['title_ka'],
                    name_ka=cur_entry['title_ka'],
                    subject=subject_math,
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
            
            
            try:
                cur_question = Question.objects.create(
                    text=cur_text,
                    question_type='single_choice',
                    question_id=int(current_question_id),
                )
            except Exception as e:
                print(f'Error creating question "{cur_text}": {e}')
                cur_question = None

            
            for topic in cur_topics:
                try:
                    cur_topic = Topic.objects.get(identifier=topic)
                except Exception as e:
                    print(f'Could not get topic "{topic}". Skipping binding question to topic {e}')
                    continue

                try:
                    QuestionToTopic.objects.create(
                        question=cur_question,
                        topic=cur_topic,
                    )
                except Exception as e:
                    print(f'Error binding question "{cur_text}" to topic {cur_topic.name}: {e}')
                    cur_question = None
            

            try:
                QuestionChoice.objects.create(
                    question = cur_question,
                    text=cur_choice_a,
                    is_correct=cur_answer=='ა'
                )

                QuestionChoice.objects.create(
                    question = cur_question,
                    text=cur_choice_b,
                    is_correct=cur_answer=='ბ'
                )

                QuestionChoice.objects.create(
                    question = cur_question,
                    text=cur_choice_c,
                    is_correct=cur_answer=='გ'
                )

                QuestionChoice.objects.create(
                    question = cur_question,
                    text=cur_choice_d,
                    is_correct=cur_answer=='დ'
                )
            except Exception as e:
                print(f'Error creating choices for question "{cur_text}": {e}')
                cur_question = None
        


    def create_video_lectures(self):
        dir_data_file = os.path.join(BASE_DIR, 'data', 'video_lectures.json')
        myfile = open(dir_data_file, encoding="utf8")
        file_contents = json.load(myfile)

        video_urls = file_contents['url']
        topics = file_contents['topic']
        subjects = file_contents['subject']
        titles = file_contents['title']
        descriptions = file_contents['description']

        assert len(video_urls) == len(topics)
        assert video_urls.keys() == topics.keys()

        video_ids = video_urls.keys()

        for cur_key in video_ids:
            cur_url = video_urls[cur_key]
            cur_topic = topics[cur_key]
            cur_subject = subjects[cur_key]
            cur_title = titles[cur_key]
            cur_description = descriptions[cur_key]
            
            try:
                cur_topic = Topic.objects.get(identifier=cur_topic)
            except Exception:
                print(f'Topic {cur_topic} does not exist!!!')
                continue
            
            try:
                cur_subject = Subject.objects.get(name=cur_subject)
            except Exception:
                print(f'Subject {cur_subject} does not exist!!!')
                continue

            try:
                cur_video = VideoLecture.objects.create(
                    url=cur_url,
                    title=cur_title,
                    description=cur_description,
                )

                VideoToTopic.objects.create(
                    video_lecture=cur_video,
                    topic=cur_topic,
                )

                VideoToSubject.objects.create(
                    video_lecture=cur_video,
                    subject=cur_subject,
                )
            except Exception as e:
                print(f'Error saving Video "{cur_url}" to database: {e}')
        


    def handle(self, *args, **options):
        # Add Subject
        self.create_subjects()
        self.create_topics()
        self.create_questions()
        self.create_video_lectures()
        # self.create_tests()

        self.create_class_levels()

        

        