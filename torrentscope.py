from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup
from torrent import Torrent

app = Flask(__name__)


@app.route('/')
def home():
    version = 0.1
    return render_template('home.html', version=version)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        query_list = query.split(' ')
        if len(query_list) > 1:
            query = "+".join(query_list)

        extra_torrent = search_extra_torrent(query)
        pirate_bay = search_piratebay(query)

        total = extra_torrent['total'] + pirate_bay['total']
        torrents = extra_torrent['results'] + pirate_bay['results']

        torrents.sort(key=lambda x: x.seeders, reverse=True)

        return render_template('results.html', total=total, torrents=torrents)
    else:
        return redirect('/')


def search_extra_torrent(query):
    html = requests.get('http://extratorrent.cc/search/?search=' + query)
    soup = BeautifulSoup(html.content)
    total = int(soup.find_all('b')[12].text)
    results = []
    if total > 0:
        r_rows = soup.find_all('tr', class_='tlr')
        z_rows = soup.find_all('tr', class_='tlz')
        all_rows = r_rows + z_rows

        for row in all_rows:
            torrent = Torrent(source='ExtraTorrent')
            attributes = row.find_all('a')[0].attrs
            title = attributes['title'].split()
            title.pop(0)
            title.pop()
            torrent.title = " ".join(title)
            download_link = attributes['href'].replace('torrent_download', 'download')
            torrent.url = 'http://extratorrent.cc' + download_link

            torrent.size = row.find_all('td')[-4].text

            if row.find('td', class_='sy'):
                torrent.seeders = int(row.find('td', class_='sy').text)
            else:
                torrent.seeders = 0

            if row.find('td', class_='ly'):
                torrent.leechers = int(row.find('td', class_='ly').text)
            else:
                torrent.leechers = 0

            results.append(torrent)

        if total > 50:
            total = 50

    return {'total': total, 'results': results}


def search_piratebay(query):
    html = requests.get('https://thepiratebay.se/search/' + query)
    soup = BeautifulSoup(html.content)
    total_phrase = soup.find_all('h2')[0].contents[1].strip()
    results = []
    if total_phrase.startswith('No hits'):
        total = 0
    else:
        total = [int(s) for s in total_phrase.split() if s.isdigit()][-1]

    if total > 0:
        rows = soup.find_all('tr')[1:]

        for row in rows:
            torrent = Torrent(source='Pirate Bay')
            td = row.find_all('td')
            torrent.title = td[1].find('a').text
            torrent.url = td[1].find_all('a')[1].attrs['href']
            torrent.seeders = int(td[2].text)
            torrent.leechers = int(td[3].text)
            torrent.size = td[1].find('font').text.split(',')[1].replace(' Size ', '')

            results.append(torrent)

    if total > 30:
        total = 30

    return {'total': total, 'results': results}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)