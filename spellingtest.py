from gtts import gTTS
from playsound import playsound
import os
import random
import time
from PyDictionary import PyDictionary
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import ety
import glob
import json
import numpy as np
from scipy.special import softmax
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys
dictionary=PyDictionary()

def play_information(text, message_on=False, sound_on=True):
    if message_on:
        print(text)
    if sound_on:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save('./info.mp3')
        playsound('./info.mp3')

def play_a_word(word, accent='co.uk', folder='mp3'):
    if accent == 'co.uk':
        fname = f'./{folder}/' + '_'.join(word.split(' ')) + '.mp3'
    else:
        fname = f'./{folder}/' + '_'.join(word.split(' ')) + f'.{accent}.mp3'
    if not os.path.exists(fname):
        tts = gTTS(text=word, lang='en', tld=accent)
        tts.save(fname)
    playsound(fname)

def get_word_list(name, fname):
    if type(fname).__name__ == 'str':
        if os.path.isfile(fname):
            fname = [fname]
        elif os.path.isdir(fname):
            fname = glob.glob(fname+'/*.txt')
    wordlist = []
    for n in fname:
        with open(n) as f:
            words = f.read().splitlines()
            words = list(filter(None, words))
            # w = sorted(words)
        wordlist.extend(words)
    return wordlist

def get_test_history(name):
    performance = []
    for test_file in glob.glob(f'./test/{name}_*'):
        with open(test_file, 'r') as f:
            results = json.load(f)
        performance.append(results)

    return performance

def practice(wordlist, performance, n_words=-1):
    total = 0
    correct = 0

    # choose n_words from word list
    # use historical test performance to adjust the probablity words being selected
    # passed word - low probability - normal * 80%
    # retried word - mid probabliy - normal * 130%
    # untested word - high probabliy - normal
    # failed word - higher probabliy - normal * 200%
    word_dic = {}
    visited = {}
    for word in wordlist:
        word_dic[word] = 1.0
        visited[word] = 0
    for results in performance:
        for k in results.keys():
            visited[k] += 1
            if results[k] == 'passed':
                word_dic[k] = word_dic[k] * 0.8
            elif results[k] == 'retried':
                word_dic[k] = word_dic[k] * 1.2
            elif results[k] == 'failed':
                word_dic[k] = word_dic[k] * 1.5

    for k in wordlist:
        word_dic[k] = word_dic[k] + 0.1 * np.log(len(performance)+1) / (visited[k]+1)

    p = softmax(list(word_dic.values()))
    if n_words > 0 and n_words < len(wordlist):
        test_samples = np.random.choice(list(word_dic.keys()), size=n_words, replace=False, p=p)
    else:
        test_samples = wordlist

    new_words_count = 0
    for k in test_samples:
        if visited[k] == 0:
            new_words_count += 1
    play_information(f'this test has {new_words_count} new words')

    test_result = {}
    for i, word in enumerate(test_samples):
        accent = 'co.uk'
        if i == len(test_samples) - 2:
            if random.random() < 0.3:
                play_information('almost done. keep going')

        retried = False
        while True:
            if total > 0:
                print(f"{total+1} - score: {correct/total*100:.1f}%: ", end='', flush=True)
            else:
                print(f"{total+1}: ", end='', flush=True)
            # time.sleep(500)
            try:
                play_a_word(word, accent)
            except:
                print('system error: ' + word)
                play_information("sorry system error. I don't know how to pronounce this word")
                break
            x = input('')
            if x.lower().strip() != word.lower().strip():
                if x == '?':  # give up. ask for answer
                    print(word, flush=True)
                    test_result[word] = 'failed'
                    break
                elif x.startswith('.'): # repeat audio
                    if x == '.':
                        accent = 'co.uk'
                    elif x == '.us':
                        accent = 'com'
                    elif x == '.au':
                        accent = 'com.au'
                    else:
                        accent = 'co.uk'
                    continue
                elif x == '?o': # ask for meaning
                    try:
                        origin = ety.origins(word)
                        if random.random() < 0.5:
                            play_information(f'{word} is originatd from {origin[0].language.name}')
                        else:
                            play_information(f'{word} is {origin[0].language.name} word')
                    except:
                        play_information(f'sorry I do not have origins of {word}')
                    continue
                elif x == '?m':
                    try:
                        meaning = dictionary.meaning(word)
                        meaning = meaning[random.choice(list(meaning.keys()))]
                        meaning = random.choice(meaning)
                        play_information(word + ' means')
                        play_information(meaning)
                    except:
                        play_information(f'sorry I do not have definition of {word}')
                    continue
                else:
                    play_information('incorrect, try again')
                    retried = True
            else:
                if random.random() > 0.7:
                    congrat = random.choice(['well done', 'good job', 'correct', 'excellent'])
                    if congrat != '':
                        play_information(congrat)
                if not retried:
                    correct += 1
                    test_result[word] = 'passed'
                else:
                    test_result[word] = 'retried'
                break

        total += 1

    return correct/total, test_result


if __name__ == '__main__':
    os.makedirs('./mp3', exist_ok=True)
    play_information("welcome to spelling test")
    if random.random() < 0.3:
        play_information("please make sure you enter your name correctly. your records will be used to optimize your test")
    play_information("what is your name")
    name = input('Enter your name: ')

    wordlist = get_word_list(name, fname='./wordlist')
    performance = get_test_history(name)

    if len(performance) > 3 and random.random() < 0.3:
        play_information(f"hi {name}. it seems you have done some tests")
        play_information(f"would you like to check your performance?")
        answer = input('Enter yes or no: ')
        if answer.lower() == 'yes':
            sys.argv.append(name)
            exec(open('stats.py').read())
            # show the word cloud
            # history = get_test_history(name)
            # word_dic = {}
            # for results in performance:
            #     for k in results.keys():
            #         if not k in word_dic.keys():
            #             word_dic[k] = 1.0
            #         if results[k] == 'passed':
            #             word_dic[k] = word_dic[k] * 0.8
            #         elif results[k] == 'retried':
            #             word_dic[k] = word_dic[k] * 1.3
            #         elif results[k] == 'failed':
            #             word_dic[k] = word_dic[k] * 2.0
            #
            # play_information(f"The big words are the ones you missed most.")
            #
            # radius = 200
            # x, y = np.ogrid[:radius*2, :radius*2]
            #
            # mask = (x - radius) ** 2 + (y - radius) ** 2 > radius ** 2
            # mask = 255 * mask.astype(int)
            #
            # wc = WordCloud(background_color="white", max_words=1000, mask=mask)
            # # generate word cloud
            # wc.generate_from_frequencies(word_dic)
            #
            # # show
            # plt.imshow(wc, interpolation="bilinear")
            # plt.axis("off")
            # plt.show()



    if random.random() < 0.5:
        play_information(f"Thank you, how many words do you like to try?")
    else:
        play_information(f"Thank you, please enter number of test words.")

    while True:
        try:
            n_words = int(input('Enter Number of Words (under 100): '))
            break
        except ValueError:
            play_information("Not a number. Please try again")

    play_information("let's get started")
    score, results = practice(wordlist=wordlist, performance=performance, n_words=n_words)
    os.makedirs('./test', exist_ok=True)
    with open(f'./test/{name}_{time.strftime("%Y%m%d-%H%M%S")}_{n_words}_{score*100:.1f}.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    play_information("Test completed")
    msg = f'final score is {score*100:.1f}%'
    play_information(msg, message_on=True)
    if score>0.9:
        if random.random() < 0.5:
            play_information('you have done an amazing job')