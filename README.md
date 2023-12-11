# Frequency dictionaries for Yomichan

High-quality frequency dictionaries ready to be imported into [Yomichan](https://foosoft.net/projects/yomichan/).

Generate frequency dictionaries from source for customization.

A frequency dictionary displays the ranked frequency (1st most frequent, 2nd most frequent, ...) of a word inside a context (written language, spoken language, web, Showa era, Heisei era, ...).

Frequency dictionaries can help language learners distinguish common words from uncommon ones.

## Features

### Latest data

The data is kept up to date with NINJAL.

### Unique dictionaries

Learn how words changed in frequency throughout history (CHJ, SHW).

Learn about frequent words on the Japanese web (NWJC).

### Careful merging of files

When compiling a frequency dictionary, one has to be careful to not count the same word occurrence twice. This would corrupt the resulting word frequency.

The dictionaries in this repo are vetted against double-counting.

### Frequency rank cap

The default dictionaries include the 50k most frequent words only. This keeps the files small and the learner focus on what is important: frequent words. Language fluency requires around 10k to 20k words of vocabulary.

## Included dictionaries

You can find the dictionaries of the following corpora as GitHub releases.

The dictionary file shares the same license as its source data.

### [Corpus of Historical Japanese (CHJ)](https://clrd.ninjal.ac.jp/chj/index.html)

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>

A corpus that covers different eras of Japanese history.

The corpus ranges from the Nara period through the Edo period and Meiji era up to the Taishō era.

To track words across eras, two dictionaries are generated:

1. A dictionary for the premodern part (Nara to Edo)
2. A dictionary for the modern part (Meiji to Taishō)

_The corpus is likely too small to generate dictionaries for each era._

### [Showa-Heisei Corpus of written Japanese](https://clrd.ninjal.ac.jp/shc/index.html)

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>

A corpus that covers the Showa and Heisei era of Japanese history.

There is one dictionary for both eras.

### [NINJAL Web Japanese Corpus (NWJC)](https://masayu-a.github.io/NWJC/)

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>

A corpus which was created by crawling the web.

## Supported dictionaries

The licence of the following corpora doesn't allow me to upload a derived dictionary.

My solution is to publish the [raw data in a separate repo](https://github.com/uncomputable/frequency-data).

Use my script to generate a frequency dictionary on your local machine.

### [Balanced Corpus of Contemporary Written Japanese (BCCWJ)](https://clrd.ninjal.ac.jp/bccwj/index.html)

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/3.0/88x31.png" /></a>

One of the largest and most popular corpora out there. It focuses on written language.

### [Corpus of Spontaneous Japanese (CSJ)](https://clrd.ninjal.ac.jp/csj/index.html)

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/3.0/88x31.png" /></a>

Another popular corpus with a focus on spoken language.

## Set up the runtime environment

### Use nix

Enter the provided nix shell.

```bash
nix-shell
```

### Use pip

Create a virtual environment and use pip to install the dependencies.

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Run the script

Run the script on the command line with the desired arguments.

```bash
python3 main.py [arguments...]
```

For example, generate the frequency dictionary for BCCWJ (short-unit words) like so:

```bash
python3 main.py bccjw BCCWJ_frequencylist_suw_ver1_1.tsv
```

There is help in case you get stuck.

```bash
python3 main.py --help
python3 main.py bccjw --help
```

## Import the dictionary

Open the Yomichan settings in your browser and click "Import Dictionary".

Select the zip file and wait for it to be processed.

The dictionary should now be working.
