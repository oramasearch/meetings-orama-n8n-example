#!/usr/bin/env python3
"""
Download and format datasets from Hugging Face.
Usage: python get_hf_dataset.py <dataset_repo> [--limit=N]
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

def format_gwenshap_sales_transcripts(repo_path: Path, output_path: Path, limit: int = None):
    """
    Format gwenshap/sales-transcripts dataset into meetings CSV format.

    Expected CSV columns:
    - id: Unique identifier
    - Item_UID: Item unique identifier
    - Meeting_UID: Meeting unique identifier
    - Transcript: Full meeting transcript text
    - Summary: Meeting summary (empty for this dataset)
    - Date: Meeting date (empty for this dataset)
    """
    transcripts_dir = repo_path / "data" / "transcripts"

    if not transcripts_dir.exists():
        print(f"Error: Transcripts directory not found at {transcripts_dir}")
        sys.exit(1)

    # Get all transcript files
    transcript_files = sorted(transcripts_dir.glob("*.txt"))

    if not transcript_files:
        print(f"Error: No transcript files found in {transcripts_dir}")
        sys.exit(1)

    # Apply limit if specified
    if limit:
        transcript_files = transcript_files[:limit]
        print(f"Processing {len(transcript_files)} files (limited from total)")
    else:
        print(f"Processing {len(transcript_files)} files")

    # Prepare output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'Item_UID', 'Meeting_UID', 'Transcript', 'Summary', 'Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, transcript_file in enumerate(transcript_files, start=1):
            # Parse filename: <company_name>_NR_transcript.txt
            filename = transcript_file.stem  # Remove .txt extension

            # Extract company name and meeting number
            # Format: CompanyName_NR_transcript
            parts = filename.split('_')
            if len(parts) >= 2 and parts[-1] == 'transcript':
                company_name = '_'.join(parts[:-2])  # Everything before _NR_transcript
                meeting_number = parts[-2]  # The NR part
            else:
                # Fallback if format is different
                company_name = filename.replace('_transcript', '')
                meeting_number = str(idx)

            meeting_uid = f"{company_name}_{meeting_number}"
            item_uid = f"item_{idx}"

            # Read transcript content
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript_content = f.read().strip()
            except Exception as e:
                print(f"Warning: Could not read {transcript_file}: {e}")
                continue

            # Write row
            writer.writerow({
                'id': idx,
                'Item_UID': item_uid,
                'Meeting_UID': meeting_uid,
                'Transcript': transcript_content,
                'Summary': '',  # No summaries in this dataset
                'Date': ''  # No dates in this dataset
            })

            print(f"  [{idx}/{len(transcript_files)}] Processed: {meeting_uid}")

    print(f"\n Successfully created {output_path}")
    print(f"  Total meetings: {len(transcript_files)}")


def extract_from_parquet(parquet_file: Path, column_mapping: dict, limit: int = None):
    """
    General function to extract data from a parquet file and map columns.

    Args:
        parquet_file: Path to the parquet file
        column_mapping: Dictionary mapping output columns to input columns or callables
                       e.g., {'id': 'source_id', 'Transcript': lambda row: row['text']}
        limit: Optional limit on number of rows to process

    Returns:
        List of dictionaries with mapped data
    """
    if not parquet_file.exists():
        print(f"Error: Parquet file not found at {parquet_file}")
        sys.exit(1)

    # Read parquet file
    df = pd.read_parquet(parquet_file)

    # Apply limit if specified
    if limit:
        df = df.head(limit)
        print(f"Processing {len(df)} rows (limited from total)")
    else:
        print(f"Processing {len(df)} rows")

    # Map columns
    mapped_data = []
    for idx, row in df.iterrows():
        mapped_row = {}
        for output_col, source in column_mapping.items():
            if callable(source):
                mapped_row[output_col] = source(row, idx)
            elif source in row:
                mapped_row[output_col] = row[source]
            else:
                mapped_row[output_col] = source  # Use as literal value
        mapped_data.append(mapped_row)

    return mapped_data


def format_meetingbank_qa_summarization_instruct(repo_path: Path, output_path: Path, limit: int = None):
    """
    Format 1-800-SHARED-TASKS/MeetingBank-QA-Summarization-Instruct dataset into meetings CSV format.

    Mapping:
    - id: <id>
    - Item_UID: item_<id>
    - Meeting_UID: meeting_<id>
    - Transcript: <prompt>
    - Summary: <summary>
    - Date: (empty)
    """
    parquet_file = repo_path / "data" / "test-00000-of-00001.parquet"

    # Define column mapping
    column_mapping = {
        'id': lambda row, idx: idx + 1,
        'Item_UID': lambda row, idx: f"item_{idx + 1}",
        'Meeting_UID': lambda row, idx: f"meeting_{idx + 1}",
        'Transcript': 'prompt',
        'Summary': 'summary',
        'Date': ''
    }

    # Extract data
    mapped_data = extract_from_parquet(parquet_file, column_mapping, limit)

    # Prepare output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'Item_UID', 'Meeting_UID', 'Transcript', 'Summary', 'Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, row in enumerate(mapped_data, start=1):
            writer.writerow(row)
            print(f"  [{idx}/{len(mapped_data)}] Processed: {row['Meeting_UID']}")

    print(f"\n Successfully created {output_path}")
    print(f"  Total meetings: {len(mapped_data)}")


def main():
    parser = argparse.ArgumentParser(
        description='Download and format Hugging Face datasets for meetings ingestion'
    )
    parser.add_argument('dataset_repo', help='Hugging Face dataset repository (e.g., gwenshap/sales-transcripts)')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of meeting entries in output')

    args = parser.parse_args()

    # Validate dataset is supported
    supported_datasets = [
        "gwenshap/sales-transcripts",
        "1-800-SHARED-TASKS/MeetingBank-QA-Summarization-Instruct"
    ]

    if args.dataset_repo not in supported_datasets:
        print(f"Error: Dataset '{args.dataset_repo}' is not supported.")
        print("\nSupported datasets:")
        for dataset in supported_datasets:
            print(f"  - {dataset}")
        sys.exit(1)

    # Get HF token from environment
    hf_token = os.getenv('HF_TOKEN')

    if not hf_token:
        print("Warning: HF_TOKEN not found in .env file. Using public access only.")
        hf_token = None

    print(f"Downloading dataset: {args.dataset_repo}")

    # Download dataset
    try:
        repo_path = Path(snapshot_download(
            repo_id=args.dataset_repo,
            repo_type="dataset",
            token=hf_token,
        ))
        print(f" Downloaded to: {repo_path}\n")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        sys.exit(1)


    # Process based on dataset repo
    dataset_name = args.dataset_repo.replace('/', '-')
    output_path = Path("hf_datasets") / f"{dataset_name}.csv"

    if args.dataset_repo == "gwenshap/sales-transcripts":
        format_gwenshap_sales_transcripts(repo_path, output_path, args.limit)
    elif args.dataset_repo == "1-800-SHARED-TASKS/MeetingBank-QA-Summarization-Instruct":
        format_meetingbank_qa_summarization_instruct(repo_path, output_path, args.limit)


if __name__ == "__main__":
    main()
