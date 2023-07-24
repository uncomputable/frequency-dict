# Frequency dictionaries for Yomichan

High-quality frequency dictionaries ready to be imported into [Yomichan](https://foosoft.net/projects/yomichan/).

Also a generator for frequency dictionaries from raw data.

A frequency dictionary displays the ranked frequency of a term inside a context, such as written or spoken language, the web or historic eras.

## Corpora

The go-to address for Japanese linguistics is [NINJAL: The National Institute for Japanese Language and Linguistics](https://www.ninjal.ac.jp/).

### [Balanced Corpus of Contemporary Written Japanese (BCCWJ)](https://clrd.ninjal.ac.jp/bccwj/index.html)

One of the largest and most popular corpora out there. It focuses on written language.

### [Corpus of Spontaneous Japanese (CSJ)](https://clrd.ninjal.ac.jp/csj/index.html)

Another popular corpus with a focus on spoken language.

### [NINJAL Web Japanese Corpus (NWJC)](https://masayu-a.github.io/NWJC/)

A relatively unknown corpus which was created by crawling the web. Compared to BCCJW (2017), this is much newer (2022).

### [Corpus of Historical Japanese (CHJ)](https://clrd.ninjal.ac.jp/chj/index.html)

A relatively unknown corpus that covers different eras of Japanese history. _(How cool is that?!)_

The corpus ranges from the Nara period through the Edo period and Meiji era up to the Taishō era.

There is a dictionary for the premodern part (Nara to Edo) and the modern part (Meji to Taishō), which prevents mixing sources from very different times.

_(We might even separate single eras, but this reduces the respective sample size and increases the total number of dictionaries.)_

## Where are the dictionaries?

You can find the NWJC and CHJ dictionaries as GitHub releases.

For BCCWJ and CSJ, as always, there are licensing issues :)

NINJAL published the data under the [CC BY-NC-ND 3.0 license](https://creativecommons.org/licenses/by-nc-nd/3.0/deed.en). This means we may not remix, transform or build upon the original and distribute the result.

My solution is to publish the [raw data in a separate repo](https://github.com/uncomputable/frequency-data). _(This data is already public on the university website.)_ You can use my script to generate a frequency dictionary on your local machine.

## Setup

### Using nix

Use the provided nix shell to set up the runtime environment.

```
nix-shell
```

### Using pip

Create a virtual environment and use pip to install the dependencies.

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Running

Run the script on the command line with the desired arguments. There is help in case you get stuck.

```
python3 main.py [arguments...]
```

For example, generate the frequency dictionary for BCCWJ (short-unit words) like so:

```
python3 main.py bccjw BCCWJ_frequencylist_suw_ver1_1.tsv
```

## Importing

Open the Yomichan settings in your browser and click _Import Dictionary_. Select the zip file and wait for it to be processed. The dictionary should now be working.
