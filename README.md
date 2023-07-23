# Frequency dictionary generator

Generate frequency dictionaries for [Yomichan](https://foosoft.net/projects/yomichan/) from raw data.

Frequency dictionaries display the ranked frequency of a term inside a context, such as written or spoken language, the web or historic eras.

The generated zip files can be directly imported into Yomichan.

## Where is the data?

As always, there are licensing issues :)

In particular, NINJAL published the data on BCCWJ and CSJ (their most popular corpora) under the [CC BY-NC-ND 3.0 license](https://creativecommons.org/licenses/by-nc-nd/3.0/deed.en). This means we may not remix, transform or build upon the original and distribute the result.

My solution is to publish the [raw data in a separate repo](https://github.com/uncomputable/frequency-data). _(This data is already public on the university website.)_ You can use my script to generate a frequency dictionary on your local machine.

Where possible, you can find a GitHub release of the generated dictionaries.

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
