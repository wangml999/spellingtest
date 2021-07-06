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

dictionary=PyDictionary()

def play_information(text, message_on=False, sound_on=True):
    if message_on:
        print(text)
    if sound_on:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save('./info.mp3')
        playsound('./info.mp3')

def play_a_word(word, folder='mp3'):
    fname = f'./{folder}/' + '_'.join(word.split(' ')) + '.mp3'
    if not os.path.exists(fname):
        tts = gTTS(text=word, lang='en', tld='co.uk')
        tts.save(fname)
    playsound(fname)


def practice(fname, n_words=-1):
    if type(fname).__name__ == 'str':
        fname = [fname]
    wordlist = []
    for n in fname:
        with open(n) as f:
            words = f.read().splitlines()
            w = sorted(words)
        wordlist.extend(words)

    total = 0
    correct = 0
    if n_words > 0 and n_words < len(wordlist):
        test_samples = random.sample(wordlist, n_words)
    else:
        test_samples = wordlist

    for i, word in enumerate(test_samples):
        if i == len(test_samples) - 2:
            if random.random() < 0.5:
                play_information('We are almost done. keep going')

        retried = False
        while True:
            if total > 0:
                print(f"{total+1} - score: {correct/total*100:.1f}%: ", end='', flush=True)
            else:
                print(f"{total+1}: ", end='', flush=True)
            # time.sleep(500)
            try:
                play_a_word(word)
            except:
                print('system error: ' + word)
                play_information("sorry system error. I don't know how to pronounce this word")
                break
            x = input('')
            if x.lower() != word.lower():
                if x == '?':  # give up. ask for answer
                    print(word, flush=True)
                    break
                elif x == '.': # repeat audio
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
                break

        total += 1
    return correct/total


if __name__ == '__main__':
    os.makedirs('./mp3', exist_ok=True)
    play_information("welcome to spelling test")
    play_information("what is your name")
    name = input('Enter your name: ')
    play_information(f"Thank you, how many words do you like to try")

    while True:
        try:
            n_words = int(input('Enter Number of Words (under 100): '))
            break
        except ValueError:
            play_information("Not a number. Please try again")

    play_information("let's get started")
    score = practice(['./wordlist/spelling_bee_page_1.txt',
              './wordlist/spelling_bee_page_2.txt'], n_words)
    play_information("Test completed")
    msg = f'final score is {score*100:.1f}%'
    play_information(msg)