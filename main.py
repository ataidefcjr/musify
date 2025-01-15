from bs4 import BeautifulSoup
import requests
import os
from concurrent.futures import ThreadPoolExecutor
import re

base_url = "https://musify.club"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
urls = []
print("Insira os URLs de https://musify.club abaixo separados por enter, linha vazia para terminar: ")
while '' not in urls:
    urls.append(input())

def format_filename(filename:str):
    caracteres_proibidos = r'[\/:*"<>|]'
    new_filename = re.sub(caracteres_proibidos, "_", filename)
    return new_filename

def format_index(link:str):
    index = link.find('div', attrs={'class':'playlist__position'}).text.strip()
    if len(index) == 1:
        return "0" + index
    return index

def download_file(url, save_path):
    try:
        for _ in range(3): 
            if os.path.exists(save_path):
                print(f"Arquivo {save_path.split('/')[1]} Já existe, pulando download.")
                return
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                print(f"Arquivo Salvo: {save_path}")
                return
            print(f"Erro ao baixar o arquivo: {save_path}, Retry: {_}")
        print(f"Abortado download de {url}")
    except Exception as e:
        print(f"Ocorreu um erro ao baixar a url: {url}")

def download_multiple_files(downloadlist, max_threads=12):
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for file in downloadlist:
            executor.submit(download_file, file['url'], file['save_path'])

if __name__ == '__main__':
    
    download_list = []
    
    for url in urls:
        
        if url == '' or not 'musify.club' in url:
            continue

        site = requests.get(url,headers=headers)
        soap = BeautifulSoup(site.content,'html.parser')
        folder_title = soap.find('header', attrs={'class':'content__title'})
        folder_title = folder_title.find('h1').text
        folder_title = format_filename(folder_title)
        band_name = soap.find('a', attrs={'itemprop' : 'byArtist'}).text.strip()
        links = soap.find_all('div', attrs={'class' : 'playlist__item'})
        for link in links:
            index = format_index(link)
            music_name = link['data-name']
            music_name = format_filename(music_name)
            a = link.find('a', attrs={'itemprop' : 'audio'})
            if a and 'href' in a.attrs:
                if 'mp3' in a['href']:
                    download_link = base_url + a['href']
                    save_path = os.path.join (folder_title , index + " - " + band_name + " - " + music_name + ".mp3")
                    download_list.append({'url': download_link, 'save_path' : save_path})
        print("Criando Diretórios, aguarde...")
        try:
            directory = os.mkdir(folder_title)
        except FileExistsError:
            print(f"Diretório {folder_title} já existe.")

    print("Iniciando os Downloads")
    download_multiple_files(download_list)
        
    print("Finalizado todos os Links!!")

        