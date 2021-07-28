import os
import glob
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd

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


if len(sys.argv) == 1:
    name = input('Enter your name: ')
else:
    name = sys.argv[-1]

wordlist = get_word_list(name, fname='./wordlist')
history = get_test_history(name)
word_dic = {}
tested_words = {}
scores = []
word_count = []
for i, results in enumerate(history):
    count = 0
    for k in results.keys():
        if not k in word_dic.keys():
            word_dic[k] = 1.0
            tested_words[k] = []
        if results[k] == 'passed':
            word_dic[k] = word_dic[k] * 0.8
            count += 1
        elif results[k] == 'retried':
            word_dic[k] = word_dic[k] * 1.3
        elif results[k] == 'failed':
            word_dic[k] = word_dic[k] * 2
        tested_words[k].append(results[k])
    scores.append(count/len(results))
    word_count.append(len(results))

for k in word_dic.keys():
    tested_words[k].append(str(word_dic[k]))

word_freq = {}
for k in word_dic:
    if word_dic[k] > 1.0:
        word_freq[k] = word_dic[k]

radius = 200
x, y = np.ogrid[:radius * 2, :radius * 2]

mask = (x - radius) ** 2 + (y - radius) ** 2 > radius ** 2
mask = 255 * mask.astype(int)

wc = WordCloud(background_color="white", max_words=1000, mask=mask)
# generate word cloud
wc.generate_from_frequencies(word_freq)

# show
fig, ax = plt.subplots(1, 2, figsize=(11,5))
ax[0].plot(scores)
ax[1].axes.yaxis.set_visible(False)
untested = len(wordlist)-len(word_dic)
tested_pass = len(word_dic) - len(word_freq)
tested_failed = len(word_freq)
ax[1].imshow(wc, interpolation="bilinear", extent=[0, len(wordlist), 0, len(wordlist)])
colors=[[.5, .5, .5], [.1, .7, .1], [.7, .1, .1]]
ax[1].bar(untested/2, 20, width=untested, bottom=-50, color=colors[0])
ax[1].bar(untested+tested_pass/2, 20, width=tested_pass, bottom=-50, color=colors[1])
ax[1].bar(untested+tested_pass+tested_failed/2, 20, width=tested_failed, bottom=-50, color=colors[2])

plt.show()
print('done')
