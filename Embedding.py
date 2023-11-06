
from sentence_transformers import SentenceTransformer
import pandas as pd
from Config import *

'''
Embedding the files extracted from the underlying database, and the results after embedding are also saved back in the table.
'''


class Embedding:
    def __init__(self):
        self.embedding_model = EMBEDDING_MODEL
        self.node_csv_path = NODE_CSV_PATH
        self.batch_size = EMBEDDING_BATCH_NUM
        self.embedding_df = None
        if self.embedding_model == 'm3e-base':
            self.model = SentenceTransformer('./m3e_base', cache_folder='./m3e_base')
        elif self.embedding_model == 'm3e-large':
            self.model = SentenceTransformer('moka-ai/m3e-large', cache_folder='./m3e_large')
        elif self.embedding_model == 'bge-large-en-v1.5':
            self.model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        elif self.embedding_model == 'bge-large-zh-v1.5':
            self.model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
        else:
            self.model = SentenceTransformer('moka-ai/m3e-base', cache_folder='./m3e_base')

    def embedding(self):
        # Check whether it's the first execution or has been executed before.
        text_csv = pd.read_csv(self.node_csv_path)
        if 'embedding' in text_csv.columns:
            # It's not the first execution, only add missing embeddings.
            text_csv = self.embedding_plain(text_csv)
        else:
            # It's the first execution, combine all text into batches.
            text_csv = self.embedding_first(text_csv)

        # Save to a CSV file and return it as a doc store.
        text_csv.to_csv(self.node_csv_path, index=False, quoting=1)
        return text_csv

    def embedding_first(self, text_csv):
        embedding_list = []
        # Split based on the batch size and calculate the total number of batches.
        text = text_csv.to_dict(orient='records')
        print(text)
        batch_size = self.batch_size
        while batch_size > 0:  # Ensure it doesn't get stuck in an infinite loop.
            end_idx = min(len(text), batch_size)
            batch = text[:end_idx]

            try:
                output = self.model(batch)
                break  # Exit the inner loop when the current batch is successful. The batch size won't exceed GPU memory.
            except RuntimeError as e:
                # Check if the error is related to GPU memory.
                if 'out of memory' in str(e):
                    print(f"Out of memory with batch size {batch_size}. Reducing batch size and trying again.")
                    batch_size //= 2  # Reduce the batch size for the current batch.
                else:
                    # If it's another error, raise it directly.
                    raise
            except:
                # Handle other unexpected errors.
                print("An unexpected error occurred.")
                break

        # Once the appropriate batch size is determined, perform the actual iteration.
        print(batch_size, "batch_size")
        num_batches = len(text) // batch_size + (1 if len(text) % batch_size != 0 else 0)
        for i in range(num_batches):
            print(i)
            start_idx = i * batch_size
            end_idx = start_idx + batch_size
            batch = text[start_idx:end_idx]
            temp_embedding = self.model.encode(batch, batch_size=batch_size, normalize_embeddings=True)
            embedding_list.extend(temp_embedding)
        text_csv['embedding'] = embedding_list
        return text_csv

    def embedding_plain(self, text_csv):
        empty_positions = text_csv[text_csv['embedding'].isnull()].index.tolist()
        for pos in empty_positions:
            print(pos)
            selected_row = text_csv.iloc[pos]

            # Drop the 'embedding' column.
            selected_row = selected_row.drop('embedding')
            print(selected_row)

            # Convert the DataFrame to JSON.
            text = selected_row.to_dict()

            # text = text_csv.loc[pos, 'embedding']
            print(text)
            embedding = self.model.encode([text], batch_size=1, normalize_embeddings=True)
            text_csv.iat[pos, text_csv.columns.get_loc('embedding')] = embedding[0]
        return text_csv

    def embedding_query(self, text):
        # Embed the query, and placing it in this class ensures the use of the same embedding model.
        return self.model.encode(text)


if __name__ == '__main__':
    e = Embedding()
    e.embedding()