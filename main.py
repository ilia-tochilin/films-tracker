import requests
import json
import bs4 as bs
import pandas as pd
import os


api_key = "AIzaSyBaTt4IgcqGPsrNgPusyTvIlcilkeDofHw"
playlist_id = "PLtLZvYaxO-ZQsZiJkfShBzJSaWCJH6U2c"
file_name = "films_list"

url = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=35&playlistId={}&key={}".format(playlist_id, api_key)


films_list = []
available_films = []
matched_films = []

try:
    df = pd.read_csv ("data.csv".format(os.getcwd()), sep="@", encoding="utf-8", usecols=['film', 'link'])
except pd.errors.EmptyDataError:
    pass


class Film:
    def __init__(self, title, year="NaN", link="NaN"):
        self.title = title
        self.year = year
        self.link = link
    
    def get_title (self):
        return self.title
    
    def get_year (self):
        return self.year

    def get_link (self):
        return self.link
    
    def __str__(self):
        return self.title + " " + self.year + " " + self.link 


''' Gets Film List From Youtube Playlist '''
def get_film_list():

    r = requests.get(url)
    t = json.loads(r.text)

    for item in t["items"]:
        if item["snippet"]["title"] == "Deleted video":
            continue
        films_list.append(
            Film(
                item["snippet"]["title"].replace("\u2014", '/-/').split('/-/')[0].lower().strip(),
                item["snippet"]["title"].replace("\u2014", '/-/').split('/-/')[1][-6:].lower().strip()[1:-1]
                )
        )


''' Outputs Film List To STDOUT '''
def printFilms():
    for film in films_list:
        try:
            print(film.get_title() + "   " + film.get_year(), end="\n")
        except:
            for char in film.get_title():
                try:
                    print(char, end="")
                except:
                    pass


''' Outputs Available Films To STDOUT '''
def print_available_films():
    for film in available_films:
        print (film.get_title() + "  " + film.get_year() + "  " + film.get_link())


''' Creates File With Film List '''
def createFile():
    with open(file_name, "w+", encoding="utf-8") as f:
        for film in films_list:
            f.write (film.get_title() + "  " + film.get_year() + "\n")


''' Gets List Of Last Available Films '''
def get_available_films(amount_of_pages=3):

    loader = '[' +  "  " * amount_of_pages + ']'

    for j in range (1, amount_of_pages + 1):


        r = requests.get("https://rezka.ag/films/best/2022/page/{}/".format(j), headers = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36' 
        }).text

        soup = bs.BeautifulSoup(r, 'html.parser')

        soup = soup.find_all("div", class_="b-content__inline_item-link")

        for i in soup:
            available_films.append (Film (
                title= i.find("a").text.lower().strip(),
                year= i.find("a")["href"][-9:-5],
                link= i.find("a")["href"]
                )
            )


        os.system("cls")
        loader = '[' + "==" * j + "  " * (amount_of_pages - j) + ']' + '\n\n'
        print ("SEARCHING: \n")
        print (loader)


''' Compares Years Of Films '''
def year_match(needed_year, available_year):
    if abs (int(needed_year) - int(available_year)) > 1:
        return False
    return True


''' Find Matches Between Available Films and Films From Youtube Playlist '''
def find_matches():

    global df

    for film in films_list:
        found = False
        for i in matched_films:
            if i.get_title() == film.get_title():
                found = True
                break
        if found:
            continue

        for film2 in available_films:
            if film.get_title() == film2.get_title() and year_match (film2.get_year(), film.get_year()):
                matched_films.append(film2)
                df = df.append ({'film' : film2.get_title(), 'link' : film2.get_link()}, ignore_index=True)


    if len(matched_films) == 0:
        print ("NO MATCHES !!!")
        return

    print ("FOUND:\n")
    max_len_title = 0
    for i in matched_films:
        if len(i.get_title()) > max_len_title:
            max_len_title = len(i.get_title())

    for i in matched_films:
        print (i.get_title().capitalize() + ' ' * (max_len_title - len(i.get_title())) + "  " + i.get_link())

    df.to_csv("data.csv", sep="@", columns=['film', 'link'], index=False)


''' Finds Films From Youtube Playlist In Local Data Storage '''
def find_in_data():

    buff = df.values.tolist()

    for film in films_list:
        for i in buff:
            if i[0].lower().strip() == film.get_title():
                matched_films.append (Film (title= i[0], link= i[1]))


''' Deletes Films Which Aren't In Film List From Local Data  '''
def trim_local_data():
    
    global df

    buff = df.values.tolist()

    for film in buff:
        found = False
        for film2 in films_list:
            if film2.get_title() == film[0]:
                found = True
                break
        if not found:
            buff.remove (film)

    df = pd.DataFrame(buff, columns=['film', 'link'])



if __name__=="__main__":
    os.system("cls")
    depth = int(input("Enter depth: "))
    get_film_list()
    trim_local_data()
    find_in_data()

    get_available_films(depth)


    find_matches()
    input("\nPress Enter to finish...")
