from bs4 import BeautifulSoup as bs4

class ParseData():
    
    def parseAttandance(content):
        soup = bs4(content, 'html.parser')

        subjects = soup.find_all('table', {'class': 'plum_fieldbig'})[1].find_all('tr', {'class': 'plum_head'})[1].find_all('td')
        subjects = [subject.text for subject in subjects[1:]]

        attandanceData = {subject: {} for subject in subjects}

        tables =  soup.find_all('table', {'class': 'plum_fieldbig'})[1:]
        tables = [table.find_all('tr') for table in tables]

        for table in tables:
            for row in table:
                if row.attrs:
                    continue

                day, *days_attandance = [td.text for td in row.find_all('td')]

                for attandance, subject in zip(days_attandance, subjects):
                    attandanceData[subject][day] = attandance
        
        return attandanceData

    def parseProfile(content):
        soup = bs4(content, 'html.parser')

        data = {}
        data_table = soup.find_all('tr', {'class': 'plum_fieldbig'})
        for row in data_table:
            try:
                key, value = row.find_all('td')
                key, value = key.get_text(), value.get_text()
                data[key] = value
            except:
                continue

        return data