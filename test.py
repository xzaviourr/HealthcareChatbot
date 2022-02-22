import pandas as pd

df = [(' hello', 1), ('wow  ', 2), (' dont ', 3)]
df = pd.DataFrame(df, columns=['name', 'number'])

print(df.iloc[0])
print(df.iloc[1])
print(df.iloc[2])

df['name'] = df['name'].str.strip()


print(df.iloc[0])
print(df.iloc[1])
print(df.iloc[2])


if 'hello' in df['name'].values:
    print("yes")