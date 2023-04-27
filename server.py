import re
import psycopg2
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

connection = None

class MyHandler(BaseHTTPRequestHandler):
    head = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>LABA</title></head><body>'
    tail = '</body></html>'

    def do_GET(self):
        with open('log.txt', 'a') as file:
            file.write(str(datetime.datetime.now()) + "\n"+ str(self.headers) + '\n')
        print(self.requestline)
        # Ваш код для обработки GET-запроса
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        match = re.search(r'(\w+)\.html', self.requestline)
        if match:
            print(match.group(1))
            if match.group(1) == 'begin':
                self.wfile.write(self.createBegin().encode())
            elif 'book' in match.group(1):
                name_book = match.group(1).replace("book_", "")
                self.wfile.write(self.getBookInfo(name_book).encode())
            elif 'author'in match.group(1):
                print(match.group(1))
                author_book = match.group(1).replace("author_", "")
                self.wfile.write(self.getAuthorInfo(author_book).encode())
            elif 'country' in match.group(1):
                country = match.group(1).replace("country_", "")
                self.wfile.write(self.getCountryInfo(country).encode())
            elif 'genre' in match.group(1):
                genre = match.group(1).replace("genre_", "")
                self.wfile.write(self.getGenreInfo(genre).encode())

    def do_POST(self):
        with open('log.txt', 'a') as file:
            file.write(str(datetime.datetime.now()) + "\n" + str(self.headers) + '\n')
        print(self.requestline)
        self.send_response(200)
        self.end_headers()
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body = body.decode('utf-8')
        parameters = body.split('&')
        values = {}
        for parameter in parameters:
            key, value = parameter.split('=')
            values[key] = value.replace("+", " ")
        action = self.requestline.split("/")[1].split(" ")[0]
        try:
            if "add-book" in action:
                self.addBook(values)
            elif "add-genre" in action:
                self.addGenre(values)
            elif "add-author" in action:
                self.addAuthor(values)
            elif "add-country" in action:
                self.addCountry(values)
            elif "update-author" in action:
                self.updateAuthor(action.split("-")[-1], values)
            elif "update-book" in action:
                self.updateBook(action.split("-")[-1], values)
            elif "update-genre" in action:
                self.updateGenre(action.split("-")[-1], values)
            elif "update-country" in action:
                self.updateCountry(action.split("-")[-1], values)
            elif "delete-author" in action:
                self.deleteAuthor(values)
            elif "delete-book" in action:
                self.deleteBook(values)
            elif "delete-genre" in action:
                self.deleteGenre(values)
            elif "delete-country" in action:
                self.deleteCountry(values)
        except Exception as e:
            connection.rollback()
            self.wfile.write(self.createBegin(str(e)).encode())


    def updateCountry(self, country, values):
        cursor = connection.cursor()
        cursor.execute("UPDATE \"Country\" SET \"Square\"  = {} WHERE \"Name\" = '{}'".format(
            values.get('square'), country.replace("_", " ")))
        cursor.execute("UPDATE \"Country\" SET \"Population\"  =  {} WHERE \"Name\" = '{}'".format(
            values.get('population'), country.replace("_", " ")))
        connection.commit()
        cursor.close()
        self.wfile.write(self.getCountryInfo(country).encode())

    def updateAuthor(self, author, values):
        cursor = connection.cursor()
        cursor.execute("UPDATE \"Author\" SET \"Country\" = '{}' WHERE \"Name\" = '{}'".format(
            values.get('country'),author.replace("_", " ")))
        connection.commit()
        cursor.close()
        self.wfile.write(self.getAuthorInfo(author).encode())

    def updateGenre(self, genre, values):
        cursor = connection.cursor()
        cursor.execute("UPDATE \"Genre\" SET \"Description\" = '{}' WHERE \"Name\" = '{}'".format(
            values.get('description'), genre.replace("_", " ")))
        connection.commit()
        cursor.close()
        self.wfile.write(self.getGenreInfo(genre).encode())

    def updateBook(self, book, values):
        cursor = connection.cursor()
        cursor.execute("UPDATE \"Book\" SET \"Genre\" = '{}' WHERE \"Name\" = '{}'".format(
            values.get('genre'), book.replace("_", " ")))
        cursor.execute("UPDATE \"Book\" SET \"Author\" = '{}' WHERE \"Name\" = '{}'".format(
            values.get('author'), book.replace("_", " ")))
        connection.commit()
        cursor.close()
        self.wfile.write(self.getBookInfo(book).encode())

    def addBook(self, values):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO \"Book\" (\"Name\", \"Author\", \"Genre\") VALUES ('{}', '{}', '{}')".format(
            values.get('title'),
            values.get('author'), values.get('genre')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def addGenre(self, values):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO \"Genre\" (\"Name\", \"Description\") VALUES ('{}', '{}')".format(
            values.get('title'), values.get('description')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def addAuthor(self, values):
        print(values)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO \"Author\" (\"Name\", \"Country\") VALUES ('{}', '{}')".format(
            values.get('title'), values.get('country')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def addCountry(self, values):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO \"Country\" (\"Name\", \"Square\", \"Population\") VALUES ('{}', '{}', '{}')".format(
            values.get('title'),
            values.get('square'), values.get('population')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def deleteBook(self, values):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM \"Book\" WHERE \"Name\" = '{}'".format(values.get('title')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def deleteAuthor(self, values):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM \"Author\" WHERE \"Name\" = '{}'".format(values.get('title')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def deleteGenre(self, values):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM \"Genre\" WHERE \"Name\" = '{}'".format(values.get('title')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def deleteCountry(self, values):
        cursor = connection.cursor()
        cursor.execute("DELETE FROM \"Country\" WHERE \"Name\" = '{}'".format(values.get('title')))
        connection.commit()
        cursor.close()
        self.wfile.write(self.createBegin().encode())

    def getBookInfo(self, name_book):
        cursor = connection.cursor()
        cursor.execute("SELECT \"Author\", \"Genre\" From  public.\"Book\" Where \"Name\" = '{}'".format(name_book.replace("_", " ")))
        book_info = cursor.fetchall()
        print(book_info)
        cursor.close()
        body = self.head
        body += '<h3>{}</h3><p>Author: <a href="http://localhost:8080/author_{}.html" target="{}">{}</a>'.format(
            name_book.replace("_", " "),book_info[0][0].replace(" ", "_"),book_info[0][0].replace(" ", "_"),book_info[0][0])
        body += '<form id="{}" action="http://localhost:8080/author_{}.html" method="get"></form></li></ul>'.format(
            name_book.replace("_", " "),book_info[0][0].replace(" ", "_"))
        body += '<p>Genre: <a href="http://localhost:8080/genre_{}.html" target="{}">{}</a>'.format(
            book_info[0][1].replace(" ", "_"), book_info[0][1].replace(" ", "_"), book_info[0][1])
        body += '<form id="{}" action="http://localhost:8080/genre_{}.html" method="get"></form></li></ul>'.format(
            book_info[0][1].replace(" ", "_"), book_info[0][1].replace(" ", "_"))
        body += '<form action="/update-book-{}" method="post" target="_self"><label for="author">Автор:</label><input type="text" id="author" name="author"><br><br>' \
                '<label for="genre">Жанр:</label><input type="text" id="genre" name="genre"><br><br>' \
                '<input type="submit" value="Изменить"></form>'.format(name_book)
        body += '<form action="http://localhost:8080/begin.html" method="GET"><input type="submit" value="Главная страница">'
        body += self.tail
        return body

    def getAuthorInfo(self, author_book):
        cursor = connection.cursor()
        cursor.execute("SELECT \"Country\" From  public.\"Author\" Where \"Name\" = '{}'".format(
            author_book.replace("_", " ")))
        author_info = cursor.fetchall()
        cursor.close()
        print(author_info)
        body = self.head
        body += '<h3>{}</h3><p>Country: <a href="http://localhost:8080/country_{}.html" target="{}">{}</a>'.format(
            author_book.replace("_", " "), author_info[0][0].replace(" ", "_"), author_info[0][0].replace(" ", "_"),
            author_info[0][0])
        body += '<form id="{}" action="http://localhost:8080/country_{}.html" method="get"></form></li></ul>'.format(
            author_book.replace("_", " "), author_info[0][0].replace(" ", "_"))
        body += '<form action="/update-author-{}" method="post" target="_self"><label for="country">Страна:</label><input type="text" id="country" name="country"><br><br>' \
                '<input type="submit" value="Изменить"></form>'.format(author_book)
        body += '<form action="http://localhost:8080/begin.html" method="GET"><input type="submit" value="Главная страница">'
        body += self.tail
        return body

    def getCountryInfo(self, country):
        cursor = connection.cursor()
        cursor.execute("SELECT \"Square\", \"Population\"  From  public.\"Country\" Where \"Name\" = '{}'".format(
            country.replace("_", " ")))
        country_info = cursor.fetchall()
        cursor.close()
        body = self.head
        body += '<h3>{}</h3><p>Square: {}'.format(country.replace("_", " "), country_info[0][0])
        body += '<p>Population: {}'.format(country_info[0][1])
        body += '<form action="/update-country-{}" method="post" target="_self"><label for="square">Площадь:</label><input type="text" id="square" name="square"><br><br>' \
                '<label for="population">Население:</label><input type="text" id="population" name="population"><br><br>' \
                '<input type="submit" value="Изменить"></form>'.format(country)
        body += '<form action="http://localhost:8080/begin.html" method="GET"><input type="submit" value="Главная страница">'
        body += self.tail
        return body

    def getGenreInfo(self, genre):
        cursor = connection.cursor()
        cursor.execute("SELECT \"Description\"  From  public.\"Genre\" Where \"Name\" = '{}'".format(
            genre.replace("_", " ")))
        genre_info = cursor.fetchall()
        cursor.close()
        body = self.head
        body += '<h3>{}</h3><p>Description: {}'.format(genre.replace("_", " "), genre_info[0][0])
        body += '<form action="/update-genre-{}" method="post" target="_self"><label for="description">Страна:</label><input type="text" id="description" name="description"><br><br>' \
                '<input type="submit" value="Изменить"></form>'.format(genre)
        body += '<form action="http://localhost:8080/begin.html" method="GET"><input type="submit" value="Главная страница">'
        body += self.tail
        return body

    def createBegin(self, error = ''):
        cursor = connection.cursor()
        cursor.execute("SELECT \"Name\" From  public.\"Book\"")
        book_name_data = cursor.fetchall()
        cursor.execute("SELECT \"Name\" From  public.\"Genre\"")
        genre_name_data = cursor.fetchall()
        cursor.execute("SELECT \"Name\" From  public.\"Country\"")
        country_name_data = cursor.fetchall()
        cursor.execute("SELECT \"Name\" From  public.\"Author\"")
        author_name_data = cursor.fetchall()
        cursor.close()
        body = self.head
        if error != "":
            body += '<h1>{}</h1>'.format(error)
        body += '<h3>Книги: </h3>'
        for name in book_name_data:
            body += '<ul><li><a href="http://localhost:8080/book_{}.html" target="{}">{}</a>'.format(name[0].replace(" ", "_"), name[0].replace(" ", "_"), name[0])
            body += '<form id="{}" action="http://localhost:8080/book_{}.html" method="get"></form></li></ul>'.format(name[0].replace(" ", "_"), name[0].replace(" ", "_"))
        body += '<h3>Добавление книги: </h3><form action="/add-book" method="post" target="_self"><label for="title">Название:</label><input type="text" id="title" name="title"><br><br>' \
               '<label for="author">Автор:</label><input type="text" id="author" name="author"><br><br><label for="genre">Жанр:</label>' \
               '<input type="text" id="genre" name="genre"><br><br>' \
               '<input type="submit" value="Добавить"></form>'
        body += '<h3>Удаление книги: </h3><form action="/delete-book" method="post" target="_self"><label for="title">Название:</label><input type="text" id="title" name="title"><br><br>' \
                '<input type="submit" value="Удалить"></form>'
        body += '<h3>Жанры: </h3>'
        for name in genre_name_data:
            body += '<ul><li><a href="http://localhost:8080/genre_{}.html" target="{}">{}</a>'.format(
                name[0].replace(" ", "_"), name[0].replace(" ", "_"), name[0])
            body += '<form id="{}" action="http://localhost:8080/genre_{}.html" method="get"></form></li></ul>'.format(
                name[0].replace(" ", "_"), name[0].replace(" ", "_"))
        body += '<h3>Добавление жанра: </h3><form action="/add-genre" method="post" target="_self"><label for="title">Название:</label><input type="text" id="title" name="title"><br><br>' \
                '<label for="description">Описание:</label><input type="text" id="description" name="description"><br><br>' \
                '<input type="submit" value="Добавить"></form>'
        body += '<h3>Удаление жанра: </h3><form action="/delete-genre" method="post" target="_self"><label for="title">Название:</label><input type="text" id="title" name="title"><br><br>' \
                '<input type="submit" value="Удалить"></form>'
        body += '<h3>Авторы: </h3>'
        for name in author_name_data:
            body += '<ul><li><a href="http://localhost:8080/author_{}.html" target="{}">{}</a>'.format(
                name[0].replace(" ", "_"), name[0].replace(" ", "_"), name[0])
            body += '<form id="{}" action="http://localhost:8080/author_{}.html" method="get"></form></li></ul>'.format(
                name[0].replace(" ", "_"), name[0].replace(" ", "_"))
        body += '<h3>Добавление автора: </h3><form action="/add-author" method="post" target="_self"><label for="title">Имя:</label><input type="text" id="title" name="title"><br><br>' \
                '<label for="country">Страна:</label><input type="text" id="country" name="country"><br><br>' \
                '<input type="submit" value="Добавить"></form>'
        body += '<h3>Удаление автора: </h3><form action="/delete-author" method="post" target="_self"><label for="title">Имя:</label><input type="text" id="title" name="title"><br><br>' \
                '<input type="submit" value="Удалить"></form>'
        body += '<h3>Страны: </h3>'
        for name in country_name_data:
            body += '<ul><li><a href="http://localhost:8080/country_{}.html" target="{}">{}</a>'.format(
                name[0].replace(" ", "_"), name[0].replace(" ", "_"), name[0])
            body += '<form id="{}" action="http://localhost:8080/country_{}.html" method="get"></form></li></ul>'.format(
                name[0].replace(" ", "_"), name[0].replace(" ", "_"))
        body += '<h3>Добавление страны: </h3><form action="/add-country" method="post" target="_self"><label for="title">Название:</label><input type="text" id="title" name="title"><br><br>' \
                '<label for="square">Площадь:</label><input type="text" id="square" name="square"><br><br><label for="population">Население:</label>' \
                '<input type="text" id="population" name="population"><br><br>' \
                '<input type="submit" value="Добавить"></form>'
        body += '<h3>Удаление страны: </h3><form action="/delete-country" method="post" target="_self"><label for="title">Название:</label><input type="text" id="title" name="title"><br><br>' \
                '<input type="submit" value="Удалить"></form>'
        body += self.tail
        return body





def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}")
    with open('log.txt', 'w') as file:
        pass
    global connection
    connection = psycopg2.connect(user="postgres",
                                  password="sTasiko1513",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="Books2.0")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
