import cv2
import os
from moviepy.editor import *
import gradio as gr
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # Default to noun if the POS tag is not found

def get_lemma(word):
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(word)
    tagged_words = nltk.pos_tag(tokens)
    lemmas = []
    for tagged_word in tagged_words:
        word = tagged_word[0]
        pos = tagged_word[1]
        wordnet_pos = get_wordnet_pos(pos)
        lemma = lemmatizer.lemmatize(word, pos=wordnet_pos)
        lemmas.append(lemma)
    return ' '.join(lemmas)

def apply_lemma_to_string(sentence):
    words = word_tokenize(sentence)
    lemmas = [get_lemma(word) for word in words]
    return ' '.join(lemmas)
    
def parse_string(string, dataset):
    parsed_list = []
    start = 0
    otherword=""
    end = len(string)
    while start < end:
        max_chunk = ""
        max_length = 0
        for chunk in VideosNames:
            if string.startswith(chunk.lower(), start) and len(chunk) > max_length:
                max_chunk = chunk
                max_length = len(chunk)
        if max_chunk:
          if len(max_chunk)>1:
            parsed_list.append(max_chunk)
            print(max_chunk)
          else:
            otherword+=max_chunk
          start += len(max_chunk)
        else:
            parsed_list.append(otherword)
            otherword=""
            start += 1
    return parsed_list


def remove_empty_values(lst):
    return [x for x in lst if x and (not isinstance(x, (str, list, dict)) or x)]


def flatten_lists(lst):
    flat_list = []
    for i in lst:
        if type(i) == list:
            flat_list.extend(flatten_lists(i))
        else:
            flat_list.append(i)
    return flat_list



path = 'Dataset'
videos = []
VideosNames = []
myList = os.listdir(path)
print(myList)
for cu_video in myList:
    current_Video = cv2.imread(f'{path}/{cu_video}')
    videos.append(current_Video)
    VideosNames.append((os.path.splitext(cu_video)[0]).replace("-"," ").lower())
print(VideosNames)

def texttoSign(text):
      
      text=text+" "
      text=text.lower()
      #text=apply_lemma_to_string(text)
      text=re.sub('[^a-z]+', ' ', text)
      framescount=0
      listofwords=parse_string(text,VideosNames)
      listofwords=remove_empty_values(listofwords)
      index=0
      for word in listofwords:
        if word not in VideosNames:
          listofwords[index]=(list(word))
          
        index+=1
      listofwords=flatten_lists(listofwords)
      clips=[]
      for i in range(len(listofwords)):

        path="Dataset/"+(listofwords[i])+".mp4"
        data=cv2.VideoCapture(path)
        framescount = data.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = data.get(cv2.CAP_PROP_FPS)
        seconds = round(framescount / fps)
        clips.append(VideoFileClip(path))
        clips[i]=clips[i].subclip(1, seconds/2)
    
      result_clip=concatenate_videoclips(clips, method='compose')
      result_clip.write_videofile("combined.mp4", fps=30)
      return "combined.mp4"
 # except:
      #  pass


demo=gr.Interface(fn=texttoSign,
                  inputs="text",
                  outputs="video",
                  title="Urdu Text To Sign",
                  description="This is a small text to sign language model based on Urdu sign langugae standards",
                 examples=[["good boy"]])

demo.launch(debug=True)