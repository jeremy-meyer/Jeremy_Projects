from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import csv

import os
os.chdir("Jeremy_Projects/mood_tracker")
load_dotenv()

client = OpenAI()
prompt = """
I have created personal short sentence journals of every day in the last year and I want to label each day with any number of relevant key words. 
I want you to label the incoming sentences ONLY using this list of key words: 

"roommates, work, exercise, insight, friends, family, spiritual, social, reflection, productive, accomplishment, coworkers, video games, solve, vacation/travel, coach, 
nature, networking, uncertanity, presentation, relax, lazy, work travel, sick, hobby, journal, games, funny, started, shopping, challenge, learning, recognition, 
adjustment, late night, organize, health, planning, self-care, stuck, stress, loneliness, teaching, movie, service, bored, adventure, conversation, comfort zone, 
irritable, day off work, headache, massage" 

You are only able to use the specific key words provided from above! Each day must have at least 1 key word. As an example, let's say I provide this journal entry:
"Interesting church lesson, talked racism and sabbath day at church, fun social activity afterwards, played card games with roomates and talked about life goals. Planned social media post and shared progress on mood tracker project" 

Then you could return this as your answer: "spiritual, roommates, games, social, presentation, hobby, reflection, conversation"
"""


# Read in journal entries
journal_raw = pd.read_csv('/Users/jeremy/downloads/Journal.csv') # Private
journal_entries = journal_raw[["date", 'summary']]
to_fill = journal_entries#[journal_entries['tags'].isna()]

# LLM call that will incorperate each journal entry
def call_llm(journal_entry):
  completion = client.chat.completions.create(
      model="gpt-4o-mini",
      temperature=0.50, # We want a little randomness, but the output needs to be clean
      messages=[
          {"role": "system", "content": "You are a helpful assistant who's task it is to label short journal entries with key words."},
          {"role": "user","content": prompt},
          {"role": "assistant","content": "Please provide the journal entry you'd like me to label, and I'll return the relevant keywords based on your criteria."},
          {"role": "user", 'content': journal_entry}
      ]
  )
  return completion.choices[0].message.content

# Continously write results to csv so results aren't lost
def write_csv(data):
    with open('journal_labeled_cache.csv', 'a', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(data)

results = dict()
for (ix, d, journal_entry) in to_fill.itertuples():
  r = call_llm(journal_entry).replace('"', '').strip()
  
  results[d] = r
  write_csv([d, r])
  print(f"{d}: {r}")



