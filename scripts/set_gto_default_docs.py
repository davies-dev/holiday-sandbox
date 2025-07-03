import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from db_access import DatabaseAccess
from config import DB_PARAMS

def set_gto_files_as_default():
    db = DatabaseAccess(**DB_PARAMS)
    print("Setting legacy GTO+ files as default for their spots...")
    with db.conn.cursor() as cur:
        # Get all spot-document links
        cur.execute("""
            SELECT l.spot_id, d.id, d.file_path, d.source_info
            FROM spot_document_links l
            JOIN study_documents d ON l.document_id = d.id
        """)
        links = cur.fetchall()
        from collections import defaultdict
        spot_to_docs = defaultdict(list)
        for spot_id, doc_id, file_path, source_info in links:
            spot_to_docs[spot_id].append((doc_id, file_path, source_info))
        updated = 0
        for spot_id, docs in spot_to_docs.items():
            # Find the GTO+ doc (by source_info or file extension)
            gto_doc_id = None
            for doc_id, file_path, source_info in docs:
                if (source_info and 'GTO' in source_info) or \
                   (file_path and file_path.lower().endswith(('.gto', '.gto+', '.gto2'))):
                    gto_doc_id = doc_id
                    break
            if gto_doc_id:
                # Set this doc as default, others as not default
                for doc_id, _, _ in docs:
                    cur.execute(
                        "UPDATE spot_document_links SET is_default = %s WHERE spot_id = %s AND document_id = %s",
                        (doc_id == gto_doc_id, spot_id, doc_id)
                    )
                updated += 1
        db.conn.commit()
    db.close()
    print(f"Updated {updated} spots to set GTO+ file as default.")

if __name__ == "__main__":
    set_gto_files_as_default() 