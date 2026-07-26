from config import ACTIAN_COLLECTION_NAME
from stages.stage_6_actian import actian_db


def reset_collection() -> None:
    if not actian_db.client.collections.exists(ACTIAN_COLLECTION_NAME):
        print(f"Collection '{ACTIAN_COLLECTION_NAME}' does not exist - nothing to delete.")
        return

    actian_db.client.collections.delete(ACTIAN_COLLECTION_NAME)
    print(f"Collection '{ACTIAN_COLLECTION_NAME}' deleted.")
    print("Run ingest.py manually to re-create it and re-ingest current documents.")


if __name__ == "__main__":
    reset_collection()
