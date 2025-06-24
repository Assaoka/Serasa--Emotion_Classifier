import os
import pandas as pd
from database import init, create_news


def main():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DATABASE_URL env var not set')
    init(db_url)

    df = pd.read_csv('resumo_economia_final.csv')
    for _, row in df.iterrows():
        create_news(
            headline=row['Titulo'],
            link=row['Link'],
            summary=row['Resumo'],
            f1=row['f1'],
            f2=row['f2'],
            f3=row['f3'],
            prompt_tokens=int(row['prompt_tokens']),
            completion_tokens=int(row['completion_tokens']),
            total_tokens=int(row['total_tokens']),
            duration=float(row['duration']),
        )


if __name__ == '__main__':
    main()
