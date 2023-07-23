import argparse
from dataclasses import dataclass
from typing import Optional, List
import re
import jaconv
from zipfile import ZipFile, ZIP_DEFLATED
from collections import defaultdict
import json
from datetime import date

KANJI = re.compile(r"[一-龯ヶ々〆]")
KANA = re.compile(r"[ぁ-ゟ゠-ヿ]")
MAX_TERM_BANK_SIZE = 10000


def chunks(lst: List, n: int) -> List[List]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@dataclass
class TermMetadata:
    text: str
    reading: Optional[str]
    rank: int

    def to_json(self) -> List:
        if self.reading:
            payload = {
                "reading": self.reading,
                "frequency": self.rank
            }
        else:
            payload = self.rank

        return [
            self.text,
            "freq",
            payload
        ]

    @classmethod
    def from_json(cls, term_meta_obj: str):
        text, _mode, reading_obj = term_meta_obj

        if "reading" in reading_obj:
            reading = reading_obj["reading"]
            frequency_obj = reading_obj["frequency"]
            rank = int(frequency_obj["value"])
        else:
            # In this case reading_obj is actually frequency_obj
            reading = text
            rank = int(reading_obj["value"])

        if not text or not reading or not rank:
            raise ValueError

        return TermMetadata(text, reading, rank)


@dataclass
class Term:
    text: str
    reading: Optional[str]

    def __hash__(self) -> hash:
        return hash((self.text, self.reading))


@dataclass
class TermOccurrences:
    """
    Counter of how many times a term has occurred.
    """
    counts: defaultdict[Term, int]
    """
    Mapping of terms to their number of occurrences.
    """

    @classmethod
    def from_frequency_list(cls, file_path: str, separator: str, text_index: int, reading_index: int,
                            frequency_index: int, skip_lines: Optional[int] = None, encoding: str = "utf-8") -> "TermOccurrences":
        """
        Count the number of term occurrences in a frequency list.

        The input file consists of lines that are ordered by term (text + reading) in lexicographical order.
        The frequency of the term is given; the rank must be calculated.

        Example columns:

        語彙素読み	語彙素	語種	語彙素ID	品詞	語形	書字形	時代	サブコーパス名	作品名	部	成立年	コアフラグ	本文種別	文体	主本文フラグ	freq

        Example line:

        スル	為る	和	19537	動詞-非自立可能	ス	す	7大正	明治・大正-小説	あらくれ		1915	1		口語	1	1
        """
        count = defaultdict(int)

        with open(file_path, "r", encoding=encoding) as f:
            for (line_index, line) in enumerate(f):
                if line_index < skip_lines:
                    continue

                split_line = line.split(separator)
                text = split_line[text_index]

                if not KANJI.search(text):
                    if not KANA.search(text):
                        # Weird entry like Arabic numbers, Latin characters or punctuation
                        continue

                    # Hiragana / Katakana word
                    reading = text
                else:
                    reading = jaconv.kata2hira(split_line[reading_index])

                occurrences = int(split_line[frequency_index])
                term = Term(text, reading)
                count[term] += occurrences

        return TermOccurrences(count)

    def overlap(self, other: "TermOccurrences") -> float:
        """
        Compute how many terms occur in both counters compared to the total number of terms.

        We disregard the number of occurrences of each term.
        """
        self_terms = set(self.counts.keys())
        other_terms = other.counts.keys()
        shared_terms = self_terms.intersection(other_terms)
        total_terms = self_terms.union(other_terms)

        return len(shared_terms) / len(total_terms)

    def overlap_different_count(self, other: "TermOccurrences"):
        for term, count in other.counts.items():
            if term in self.counts:
                difference = abs(self.counts[term] - count)
                if difference > 0:
                    print(term, difference)

    def unify_distinct(self, other: "TermOccurrences"):
        """
        Add the counts from another counter to the counts of self.

        **Assumes that both counters count distinct term occurrences!**

        If this premise is violated, the same occurrence might be counted twice!
        """
        for term, count in other.counts.items():
            self.counts[term] += count

    def unify_conservative_overlap(self, other: "TermOccurrences"):
        """
        Add the counts from another counter to the counts of self.

        **Assumes that any numeric overlap in counts is an overlap in actual term occurrences!**

        If self counts some term N times and other counts the term M times,
        then min(N, M) is the numeric overlap.
        We assume that these min(N, M) occurrences are the same for both counters *(in reality they might not be)*.

        The conservative approach is to take max(N, M) as the total count.
        This makes it impossible that any term occurrence is counted twice.

        If the premise is violated, some occurrences might not be counted at all.
        """
        for term, count in other.counts.items():
            total_count = max(self.counts[term], count)
            self.counts[term] = total_count

    def to_rank_list(self) -> "RankList":
        ranked_terms = sorted(self.counts.items(), key=lambda x: -x[1])
        term_meta_bank = list()

        for rank, (term, occurrences) in enumerate(ranked_terms):
            term_meta = TermMetadata(term.text, term.reading, rank)
            term_meta_bank.append(term_meta)

        return RankList(term_meta_bank)


@dataclass
class RankList:
    term_meta_bank: List[TermMetadata]

    @classmethod
    def from_rank_list(cls, file_path: str, separator: str, text_index: int, reading_index: int,
                       skip_lines: Optional[int] = None, max_entries: Optional[int] = None, encoding: str = "utf-8") -> "RankList":
        """
        The input file consists of lines that are ordered by rank (n-th most common term) in increasing order.

        Example columns:

        rank	lForm	lemma	pos	subLemma	wType	frequency	pmw

        Example line:

        12	スル	為る	動詞-非自立可能		和	1879056	17609.02373814957
        """
        term_meta_bank = list()

        with open(file_path, "r", encoding=encoding) as f:
            for (line_index, line) in enumerate(f):
                if line_index < skip_lines:
                    continue
                if len(term_meta_bank) >= max_entries:
                    break

                split_line = line.split(separator)
                text = split_line[text_index]

                if not KANJI.search(text):
                    if not KANA.search(text):
                        # Weird entry like Arabic numbers, Latin characters or punctuation
                        continue

                    # Hiragana / Katakana word
                    reading = text
                elif reading_index:
                    reading = jaconv.kata2hira(split_line[reading_index])
                else:
                    reading = None

                term_meta = TermMetadata(text, reading, line_index + 1)
                term_meta_bank.append(term_meta)

        return RankList(term_meta_bank)

    @classmethod
    def from_zip(cls, zip_file: ZipFile, max_entries: Optional[int] = None) -> "RankList":
        term_meta_bank = list()
        bank_file_names = [f for f in zip_file.namelist() if "term_meta_bank" in f]

        for bank_file_name in bank_file_names:
            with zip_file.open(bank_file_name, "r") as f:
                bank_obj = json.load(f)

                for term_meta_obj in bank_obj:
                    if len(term_meta_bank) >= max_entries:
                        return RankList(term_meta_bank)

                    term_meta_data = TermMetadata.from_json(term_meta_obj)
                    term_meta_bank.append(term_meta_data)

        return RankList(term_meta_bank)

    def to_chunked_json(self) -> List[List]:
        bank_objects = list()

        for term_meta_bank in chunks(self.term_meta_bank, MAX_TERM_BANK_SIZE):
            bank_obj = list()

            for term_metadata in term_meta_bank:
                bank_obj.append(term_metadata.to_json())

            bank_objects.append(bank_obj)

        return bank_objects


class MetaDictionary:
    rank_list: RankList
    title: str
    revision: str
    author: Optional[str]
    url: Optional[str]
    description: Optional[str]
    attribution: Optional[str]

    def __init__(self, rank_list: RankList, title: str, revision: str, author: Optional[str] = None,
                 url: Optional[str] = None, description: Optional[str] = None, attribution: Optional[str] = None):
        self.rank_list = rank_list
        self.title = title
        self.revision = revision
        self.author = author
        self.url = url
        self.description = description
        self.attribution = attribution

    def to_zip(self, file_path: str):
        with ZipFile(file_path, mode="w", compression=ZIP_DEFLATED) as zip_file:
            self._index_to_zip(zip_file)
            self._term_meta_banks_to_zip(zip_file)

        print("Finished {}".format(file_path))

    def _index_to_zip(self, zip_file: ZipFile):
        index_obj = {
            "title": self.title,
            "format": 3,
            "revision": self.revision,
            "sequenced": False,
            "frequencyMode": "rank-based",
        }

        if self.author:
            index_obj["author"] = self.author
        if self.url:
            index_obj["url"] = self.url
        if self.description:
            index_obj["description"] = self.description
        if self.attribution:
            index_obj["attribution"] = self.attribution

        index_json_str = json.dumps(index_obj, ensure_ascii=False)
        zip_file.writestr("index.json", index_json_str)

    def _term_meta_banks_to_zip(self, zip_file: ZipFile):
        bank_objects = self.rank_list.to_chunked_json()

        for (bank_index, bank_obj) in enumerate(bank_objects):
            bank_file_name = "term_meta_bank_{}.json".format(bank_index + 1)
            bank_json_str = json.dumps(bank_obj, sort_keys=True, ensure_ascii=False)
            zip_file.writestr(bank_file_name, bank_json_str)

    @classmethod
    def from_zip(cls, file_path: str, max_entries: Optional[int] = None) -> "MetaDictionary":
        with ZipFile(file_path, mode="r") as zip_file:
            rank_list = RankList.from_zip(zip_file, max_entries)
            dictionary = MetaDictionary(rank_list, "", "")
            dictionary._load_index(zip_file)

            return dictionary

    def _load_index(self, zip_file: ZipFile):
        with zip_file.open("index.json") as f:
            index = json.load(f)
            self.title = index["title"]
            self.revision = index["revision"]

            if "author" in index:
                self.author = index["author"]
            if "url" in index:
                self.url = index["url"]
            if "description" in index:
                self.description = index["description"]
            if "attribution" in index:
                self.attribution = index["attribution"]


def nwjc(args: argparse.Namespace):
    """
    NINJAL Web Japanese Corpus

    File:

    NWJC_frequencylist_suw_ver2022_02.tsv

    File source:

    https://repository.ninjal.ac.jp/
    Go to 言語資源 → 国語研日本語ウェブコーパス → 『国語研日本語ウェブコーパス』中納言搭載データ語彙表
    """
    rank_list = RankList.from_rank_list(
        args.file_suw, separator="\t", text_index=2, reading_index=1, skip_lines=1, max_entries=80000)
    dictionary = MetaDictionary(
        rank_list, "ウェブ", "src v2022-02 yomi v{}".format(date.today().isoformat()),
        "NINJAL, uncomputable", "https://github.com/uncomputable/frequency-dict",
        """『国語研日本語ウェブコーパス（NWJC）』はウェブを母集団として100億語規模を目標として構築した日本語コーパスです。 
        
        https://masayu-a.github.io/NWJC/""",
        "CC BY 4.0 https://creativecommons.org/licenses/by/4.0/deed.ja")
    dictionary.to_zip("NWJC.zip")


def chj_modern(args: argparse.Namespace):
    """
    Corpus of Historical Japanese: Modern Era

    Files:

    CHJ-LEX_SUW_2022.3_modern_nonmag.csv
    CHJ-LEX_SUW_2022.3_modern_mag.csv

    File source:

    https://repository.ninjal.ac.jp/
    Go to 言語資源 → 日本語歴史コーパス → 『日本語歴史コーパス』統合語彙表（バージョン2022.03）
    """
    occurrences1 = TermOccurrences.from_frequency_list(
        args.file_suw[0], separator="\t", text_index=1, reading_index=0, frequency_index=16, skip_lines=1, encoding="utf-16")
    occurrences2 = TermOccurrences.from_frequency_list(
        args.file_suw[1], separator="\t", text_index=1, reading_index=0, frequency_index=16, skip_lines=1, encoding="utf-16")
    occurrences1.unify_distinct(occurrences2)

    rank_list = occurrences1.to_rank_list()
    dictionary = MetaDictionary(
        rank_list, "明治〜大正", "src v2022-03 yomi v{}".format(date.today().isoformat()),
        "NINJAL, uncomputable", "https://github.com/uncomputable/frequency-dict",
        """ 『日本語歴史コーパス（CHJ）』は、デジタル時代における日本語史研究の基礎資料として開発を進めているコーパスです。
        
        明治・大正編：雑誌／教科書／明治初期口語資料／近代小説／新聞／落語SP盤
        
        https://clrd.ninjal.ac.jp/chj/index.html""",
        "CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja"
        )
    dictionary.to_zip("CHJ_modern.zip")


def chj_premodern(args: argparse.Namespace):
    """
    Corpus of Historical Japanese: Premodern Era

    Files:

    CHJ-LEX_SUW_2022.3_premodern.csv
    CHJ-LEX_LUW_2022.3.csv

    File source:

    https://repository.ninjal.ac.jp/
    Go to 言語資源 → 日本語歴史コーパス → 『日本語歴史コーパス』統合語彙表（バージョン2022.03）
    """
    occurrences1 = TermOccurrences.from_frequency_list(
        args.file_suw, separator="\t", text_index=1, reading_index=0, frequency_index=16, skip_lines=1, encoding="utf-16")

    if args.file_luw:
        occurrences2 = TermOccurrences.from_frequency_list(
            args.file_luw, separator="\t", text_index=1, reading_index=0, frequency_index=13, skip_lines=1, encoding="utf-16")
        occurrences1.unify_conservative_overlap(occurrences2)

    rank_list = occurrences1.to_rank_list()
    suw_luw_version = "SUW+LUW" if args.file_luw else "SUW"
    dictionary = MetaDictionary(
        rank_list, "奈良〜江戸", "src v2022-03 yomi v{} {}".format(date.today().isoformat(), suw_luw_version),
        "NINJAL, uncomputable", "https://github.com/uncomputable/frequency-dict",
        """『日本語歴史コーパス（CHJ）』は、デジタル時代における日本語史研究の基礎資料として開発を進めているコーパスです。
        
        奈良時代編：万葉集／宣命／祝詞
        平安時代編：仮名文学／訓点資料
        鎌倉時代編：説話・随筆／日記・紀行／軍記
        室町時代編：狂言／キリシタン資料
        江戸時代編：洒落本／人情本／近松浄瑠璃／随筆・紀行
        
        https://clrd.ninjal.ac.jp/chj/index.html""",
        "CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ja"
        )
    dictionary.to_zip("CHJ_premodern.zip")


def bccwj(args: argparse.Namespace):
    """
    Balanced Corpus of Contemporary Written Japanese

    Files:

    BCCWJ_frequencylist_suw_ver1_1.tsv
    BCCWJ_frequencylist_luw2_ver1_1.tsv

    File source:

    https://repository.ninjal.ac.jp/
    Go to 言語資源 → 現代日本語書き言葉均衡コーパス → 『現代日本語書き言葉均衡コーパス』短単位語彙表(Version 1.1)
    """
    occurrences1 = TermOccurrences.from_frequency_list(
        args.file_suw, separator="\t", text_index=1, reading_index=0, frequency_index=6, skip_lines=0)

    if args.file_luw:
        occurrences2 = TermOccurrences.from_frequency_list(
            args.file_luw, separator="\t", text_index=2, reading_index=1, frequency_index=6, skip_lines=1)
        occurrences1.unify_conservative_overlap(occurrences2)

    rank_list = occurrences1.to_rank_list()
    suw_luw_version = "SUW+LUW" if args.file_luw else "SUW"
    dictionary = MetaDictionary(
        rank_list, "書き言葉", "src v1.1 (2017-12) yomi v{} {}".format(date.today().isoformat(), suw_luw_version),
        "NINJAL, uncomputable", "https://github.com/uncomputable/frequency-dict",
        """『現代日本語書き言葉均衡コーパス（BCCWJ）』は、現代日本語の書き言葉の全体像を把握するために構築したコーパスであり、現在、日本語について入手可能な唯一の均衡コーパスです。
        
        https://clrd.ninjal.ac.jp/bccwj/index.html""",
        "CC BY-NC-ND 3.0 https://creativecommons.org/licenses/by-nc-nd/3.0/deed.ja"
        )
    dictionary.to_zip("BCCWJ.zip")


def csj(args: argparse.Namespace):
    """
    Corpus of Spontaneous Japanese

    File:

    CSJ_frequencylist_suw_ver201803.tsv

    File source:

    https://repository.ninjal.ac.jp/
    Go to 言語資源 → 日本語話し言葉コーパス → 『日本語話し言葉コーパス』語彙表(Version 201803)
    """
    rank_list = RankList.from_rank_list(
        args.file_suw, separator="\t", text_index=2, reading_index=1, skip_lines=1, max_entries=80000)
    dictionary = MetaDictionary(
        rank_list, "話し言葉", "src v2018-03 yomi v{}".format(date.today().isoformat()),
        "NINJAL, uncomputable", "https://github.com/uncomputable/frequency-dict",
        """『日本語話し言葉コーパス（CSJ）』は、日本語の自発音声を大量にあつめて多くの研究用情報を付加した話し言葉研究用のデータベースであり、国立国語研究所・ 情報通信研究機構（旧通信総合研究所）・ 東京工業大学 が共同開発した、質・量ともに世界最高水準の話し言葉データベースです。

        https://clrd.ninjal.ac.jp/csj/index.html""",
        "CC BY-NC-ND 3.0 https://creativecommons.org/licenses/by-nc-nd/3.0/deed.ja"
    )
    dictionary.to_zip("CSJ.zip")


def convert_jpdb(args: argparse.Namespace):
    """
    Corpus based on JPDB

    File:

    Freq.JPDB_2022-05-10T03_27_02.930Z.zip

    File source:

    https://github.com/MarvNC/jpdb-freq-list
    """
    dictionary = MetaDictionary.from_zip(args.file, max_entries=80000)
    dictionary.to_zip("JPDB.zip")


# TODO: Substitute 重重 for 重々 in to_zip function
# FIXME: NWJC: 読み occurs multiple times as different parts of speech
# FIXME: Some words (の, 場[ば]) occur multiple times in the same frequency file!
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate yomichan dictionaries from raw frequency lists.")
    subparsers = parser.add_subparsers(required=True)

    parser_a = subparsers.add_parser("bccwj", help="Balanced Corpus of Contemporary Written Japanese")
    parser_a.add_argument("file_suw", type=str, help="Path to BCCWJ_frequencylist_suw_ver1_1.tsv")
    parser_a.add_argument("file_luw", nargs="?", type=str, help="Path to BCCWJ_frequencylist_luw2_ver1_1.tsv")
    parser_a.set_defaults(func=bccwj)

    parser_b = subparsers.add_parser("csj", help="Corpus of Spontaneous Japanese")
    parser_b.add_argument("file_suw", type=str, help="Path to CSJ_frequencylist_suw_ver201803.tsv")
    parser_b.set_defaults(func=csj)

    parser_c = subparsers.add_parser("nwjc", help="NINJAL Web Japanese Corpus")
    parser_c.add_argument("file_suw", type=str, help="Path to NWJC_frequencylist_suw_ver2022_02.tsv")
    parser_c.set_defaults(func=nwjc)

    parser_d = subparsers.add_parser("chj_premodern", help=" Corpus of Historical Japanese: Premodern Era")
    parser_d.add_argument("file_suw", type=str, help="Path to CHJ-LEX_SUW_2022.3_premodern.csv")
    parser_d.add_argument("file_luw", nargs="?", type=str, help="Path to CHJ-LEX_LUW_2022.3.csv")
    parser_d.set_defaults(func=chj_premodern)

    parser_e = subparsers.add_parser("chj_modern", help="Corpus of Historical Japanese: Modern Era")
    parser_e.add_argument("file_suw", nargs=2, type=str, help="Path to CHJ-LEX_SUW_2022.3_modern_{nonmag,mag}.csv")
    parser_e.set_defaults(func=chj_modern)

    parser_f = subparsers.add_parser("jpdb", help="Corpus based on JPDB [convert yomichan dictionary]")
    parser_f.add_argument("file", type=str, help="Path to Freq.JPDB_2022-05-10T03_27_02.930Z.zip")
    parser_f.set_defaults(func=convert_jpdb)

    args = parser.parse_args()
    args.func(args)
