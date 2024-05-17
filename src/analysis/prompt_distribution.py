import json
import os
from collections import Counter
import pandas as pd
import sys
import timeit

# Set the parent directory to the directory containing `src`
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))

# Add the src directory to the sys.path
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Now, we can import modules from the src directory
try:
    from collection_mapper import COLLECTION_FN_MAPPER
    from downloader import Downloader
    from download_and_filter import get_collection_to_uid_and_filter_ids
    from helpers import io
    from helpers import constants
except ModuleNotFoundError as e:
    print("ModuleNotFoundError:", e)
    sys.exit(1)

collection_name = "WildChat"
DATA_DIR = '/Users/nayan/Documents/dpi/data_summaries'
assert os.path.exists(DATA_DIR), f"Error: {DATA_DIR} does not exist"
all_collection_infos = {r["Unique Dataset Identifier"]                        : r for r in io.read_data_summary_json(DATA_DIR)}
template_spec_filepath = os.path.join(DATA_DIR, '_template_spec.yaml')
assert os.path.exists(
    template_spec_filepath), f"Error: `{template_spec_filepath}` file is missing or corrupted"
template_spec = io.read_yaml(template_spec_filepath)

# Open data collection metadata file
collection_filepath = os.path.join(DATA_DIR, f"{collection_name}.json")
assert os.path.exists(
    collection_filepath), f"There is no collection file at {collection_filepath}"
collection_info = io.read_json(collection_filepath)

collection_name = collection_info[list(
    collection_info.keys())[0]]["Collection"]
uid_to_filter_ids = {uid: dset_info['Dataset Filter IDs']
                     for uid, dset_info in collection_info.items()}

# Load configurations and run the downloader/preparer
data_summary_df = pd.DataFrame(list(all_collection_infos.values())).fillna("")
uid_task_keys = get_collection_to_uid_and_filter_ids(data_summary_df)[
    collection_name]

downloader_args = COLLECTION_FN_MAPPER[collection_name]
downloader_args.update({"uid_key_mapper": uid_task_keys})
downloader = Downloader(
    name=collection_name,
    **downloader_args
)
all_acceptable_filter_ids = [
    v for vs in uid_to_filter_ids.values() for v in vs]

# Time the download and prepare process
start_time = timeit.default_timer()
downloader.download_and_prepare(all_acceptable_filter_ids, debug=False)
elapsed_time = timeit.default_timer() - start_time

print(f"Download and preparation completed in {elapsed_time:.2f} seconds.")
