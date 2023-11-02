data = {'1': 1, '2': 2, '4': 4, '5': 5}

for key in range(5):
    if data.get(f'{key}', None) is None:
        pass
    else:
        print(data[f"{key}"])
