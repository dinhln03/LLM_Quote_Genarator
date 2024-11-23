import json
from pathlib import Path


def merge_file(
    input_path_dir="../../data",
    output_path_dir="../../merged_data/translated_quote.json",
):

    result = []

    directory = Path(input_path_dir)

    for json_file in directory.glob("*.json"):

        if json_file.is_file():

            with open(json_file, "r") as f:

                data = json.load(f)

                result.extend(data)

    with open(output_path_dir, "w") as f:

        json.dump(result, f, indent=2)


if __name__ == "__main__":

    merge_file()
