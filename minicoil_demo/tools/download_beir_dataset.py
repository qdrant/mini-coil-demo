from beir import util
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="Name of the BEIR dataset to download")
    args = parser.parse_args()

    dataset = args.dataset
    url = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip".format(dataset)
    util.download_and_unzip(url, "data")

if __name__ == "__main__":
    main()