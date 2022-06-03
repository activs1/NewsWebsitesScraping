import numpy as np
import pandas as pd
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from scrapy.crawler import CrawlerProcess
from spiders.Tvn24Spider import Tvn24Spider
from spiders.TVPInfoSpider import TvpinfoSpider

stopwords_list = list(pd.read_csv('most_used_words.csv')['word']) + list(STOPWORDS) \
                 + ['jest', 'będzie', 'zobacz', 'więcej', 'oglądaj', 'wiesz', 'więcej',
                    'polub', 'nas', 'polub nas', 'pic', 'źródło', 'pap', 'źródło pap',
                    'tym', 'portal', 'było', 'mnie', 'info', 'jakie', 'aplikację', 'mobilną',
                    'wieszwiecej', 'Polub', 'twitter', 'dodał', 'można', 'wiesz', 'wiecej',
                    'był', 'była', 'mają', 'tych', 'która', 'który', 'którzy', 'nich', 'WIDEO',
                    'wieszwiecejPolub', 'kolejne', 'chodzi', 'wynika', 'przyznał', 'będziemy',
                    'mówił', 'których', 'Pobierz', 'mamy', 'powiedział', 'tys', 'które', 'będą',
                    'poinformował', 'ocenił', 'napisał', 'https', 'podkreślił', 'tej sprawie', 'tej', 'sprawie',
                    'stwierdził', 'zaznaczył', 'roku', 'innymi', 'wcześniej', 'mówi', 'którym',
                    'niego', 'mówiła', 'której', 'miała', 'możemy', 'została', 'informuje', 'takie',
                    'przekazał', 'pytany', 'jedna', 'dalej', 'dodała', 'miały', 'stało', 'zdaniem', 'wszystkich',
                    'odpowiedział', 'odpowiedziała', 'zostaniw', 'został', 'powiedziała', 'mogą', 'dodaje',
                    'zostały', 'zostanie', 'nam', 'red', 'jesteśmy', 'którą', 'związku', 'one', 'chce',
                    ]

def shorten(value):
    if value == 'Szczepienia przeciwko COVID-19 - najważniejsze informacje':
        return 'Szczepienia COVID-19 najważniejsze informacje'
    return value

def count_occurences(val, l):
    count = 0
    for x in l:
        if x == val:
            count += 1
    return count


def run_scrapers(scrapers):
    for scraper in scrapers:
        process = CrawlerProcess()
        process.crawl(scraper)
    process.start()


def authors_and_tags(csv, limit_authors=5, limit_tags=3):
    df = pd.read_csv(csv)
    author_to_tags = {k : [] for k in set(df['ArticleAuthor'])}
    author_to_occurences = {k : 0 for k in set(df['ArticleAuthor'])}
    tags_list = []
    for article_tags in df['ArticleTags']:
        t = str(article_tags).split(',')
        for el in t:
            tags_list.append(el)
    unique_tags = set(tags_list)
    # print(author_to_tags)

    for index, row in df.iterrows():
        author_to_tags[row['ArticleAuthor']] += (str(row['ArticleTags']).split(','))
        author_to_occurences[row['ArticleAuthor']] += 1

    author_to_tags = {author: [tag for tag in author_to_tags[author]] for author in author_to_tags.keys()}
    # print(author_to_tags)
    # print(author_to_occurences)

    authors_sorted_by_occurence = dict(sorted(author_to_occurences.items(), key=lambda item: item[1], reverse=True))
    # print(authors_sorted_by_occurence)
    authors_to_tags_to_tag_occurences = {author: {tag: count_occurences(tag, author_to_tags[author]) for tag in author_to_tags[author]} for author in authors_sorted_by_occurence.keys()}
    for author in authors_to_tags_to_tag_occurences:
        authors_to_tags_to_tag_occurences[author] = dict(sorted(authors_to_tags_to_tag_occurences[author].items(), key=lambda item: item[1], reverse=True))
    # print(authors_to_tags_to_tag_occurences)

    authors_limited = list(authors_to_tags_to_tag_occurences.keys())[0:limit_authors]
    tags_limited = [[tag for tag in list(authors_to_tags_to_tag_occurences[author].keys())[0:limit_tags]] for author in authors_limited]
    values_limited = [[value for value in list(authors_to_tags_to_tag_occurences[author].values())[0:limit_tags]] for author in authors_limited]
    # print(authors_limited)
    # print(tags_limited)
    # print(values_limited)

    fig = plt.figure(100, figsize=(10, 7))
    plt.suptitle(f"Wykaz najczęściej używanych tagów \nprzez 5 najczęściej publikujących autorów na stronie {csv.replace('Articles.csv', '')}")
    plt.subplot(321)
    plt.title('Autor: ' + authors_limited[0])
    plt.bar(tags_limited[0], values_limited[0], width=0.45)
    plt.subplot(322)
    plt.title('Autor: ' + authors_limited[1])
    plt.bar(tags_limited[1], values_limited[1], width=0.45)
    plt.subplot(323)
    plt.title('Autor: ' + authors_limited[2])
    plt.bar(tags_limited[2], values_limited[2], width=0.45)
    plt.subplot(324)
    plt.title('Autor: ' + authors_limited[3])
    plt.bar(tags_limited[3], values_limited[3], width=0.45)
    plt.subplot(325)
    plt.title('Autor: ' + authors_limited[4])
    plt.bar(tags_limited[4], values_limited[4], width=0.45)
    plt.subplots_adjust(wspace=0.3, hspace=0.40)
    plt.show()


def plot_tags_occurences(tags_dict, website, first_date, last_date, limit=20):
    sorted_dict = dict(sorted(tags_dict.items(), key=lambda item: item[1], reverse=True))
    del sorted_dict['nan']
    limit_keys = list(sorted_dict.keys())[0:limit]
    values = list(sorted_dict.values())[0:limit]
    plt.figure(figsize=(10, 7))
    plt.title(f'Wykaz najczęsciej używanych tagów w kategorii Polska\nna stronie {website} w okresie {first_date.strftime("%Y-%m-%d")} - {last_date.strftime("%Y-%m-%d")}\n{limit} pierwszych')
    plt.bar([shorten(key) for key in limit_keys], values, color=(0.3, 0.6, 0.8))
    plt.subplots_adjust(bottom=0.40)
    plt.xticks(rotation=90)
    plt.yticks(np.arange(0, max(values)+2, 40))
    plt.show()


def process_csvs(csvs):
    for csv in csvs:
        print("Now processing: " + csv)
        df = pd.read_csv(csv)
        tags = df['ArticleTags']
        authors = df['ArticleAuthor']
        author_occurences = []
        for author in set(authors):
            author_occurences.append(count_occurences(author, authors))
        texts = df['ArticleText']
        dates = df['ArticleDate']
        new_dates = [datetime.strptime(str(d if not pd.isna(d) else "01.01.1000"), '%d.%M.%Y') for d in dates]
        new_dates = [date for date in new_dates if date != datetime.strptime("01.01.1000", '%d.%M.%Y')]
        if min(new_dates).year < 2019:
            new_dates.remove(min(new_dates))
        first_date = min(new_dates)
        last_date = max(new_dates)

        authors_and_tags(csv)

        # Process tags
        tags_list = []
        for article_tags in tags:
            t = str(article_tags).split(',')
            for el in t:
                tags_list.append(el)
        unique_tags = set(tags_list)
        tags_occurences = {}
        for unique_tag in unique_tags:
            tags_occurences[unique_tag] = count_occurences(unique_tag, tags_list)
        plot_tags_occurences(tags_occurences, csv.replace('Articles.csv', ''), first_date, last_date)

        # Process text
        appended_text = ' '.join([str(text).strip() for text in texts])
        # Wordcloud
        wd = WordCloud(min_word_length=3, width=1000, height=800, stopwords=stopwords_list).generate(appended_text)
        plt.imshow(wd, interpolation='bilinear')
        plt.title(f"Wordcloud na podstawie tekstów artykułów ze strony {csv.replace('Articles.csv', '')}\n Ilość artykułów: 5000")
        plt.axis('off')
        plt.show()


def main():
    # spiders = [Tvn24Spider, TvpinfoSpider]
    # run_scrapers(spiders)

    csvs = ['Tvn24Articles.csv', 'TVPInfoArticles.csv']
    process_csvs(csvs)


if __name__ == "__main__":
    main()
