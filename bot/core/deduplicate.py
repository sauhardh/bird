from sentence_transformers import SentenceTransformer, util


class Deduplicate:
    model: SentenceTransformer

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def duplicate_index(self, titles: list, threshold: float = 0.81) -> list:
        embeddings = self.model.encode(titles, convert_to_tensor=True)
        keep_indexes = []
        reject_indexes = []

        for i in range(len(titles)):
            is_duplicate = False

            for j in keep_indexes:
                sim = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
                print("sim", sim)

                if sim > threshold:
                    is_duplicate = True
                    reject_indexes.append(i)
                    break

            if not is_duplicate:
                keep_indexes.append(i)

        print("rejected indexes are", reject_indexes)
        return reject_indexes
