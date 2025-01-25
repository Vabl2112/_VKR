strings = []
with open('unconverted_cities_rassilka.txt', 'r', encoding='UTF-8') as file:
    for i in file:
        if len(i.strip()) != 0 and i.strip() != 'Рейсы за границу:':
            strings.append(i.strip().replace('Минеральные Воды', 'Минводы'))

for i in strings:
    print(i)

unconverted_cities = []
for i in range(len(strings))[::5]:
    try:
        unconverted_cities.append([
            strings[i+1].replace('Из г. ', '').replace(',', ''),
            '→' if strings[i+2][0] == 'в' else '⇄',
            strings[i],
            strings[i + 3].replace('от ', '').replace('₽', '').replace(' ', '')
        ])
    except:pass

with open('cities.txt', 'w', encoding='UTF-8') as file:
    for i in unconverted_cities:
        file.write(' '.join(i)+'\n')