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

        return render_template('results.html', extra_torrent=extra_torrent)
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
            torrent = Torrent()
            attributes = row.find_all('a')[0].attrs
            torrent.title = attributes['title']
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
            results.sort(key=lambda x: x.seeders, reverse=True)

    return {'total': total, 'results': results}


def search_piratebay(query):
    pass


if __name__ == '__main__':
    app.run(debug=True)