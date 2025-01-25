unconverted_cities = []
with open('unconverted_cities.txt', 'r', encoding='UTF-8') as file:
    for i in file:
        a = i.strip().replace('Минеральные Воды', 'МинВоды').replace(' - ', ' ').split()
        if len(a) <= 0: continue
        if a[-3] == 'в': unconverted_cities.append([a[0], '→', a[1], a[3]])
        else: unconverted_cities.append([a[0], '⇄', a[1], a[3]])
with open('cities.txt', 'w', encoding='UTF-8') as file:
    for i in unconverted_cities:
        file.write(' '.join(i)+'\n')


