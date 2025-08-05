import requests
import os
from pathlib import Path
from urllib.parse import urlparse


def download_pdf(url, save_path, filename=None, timeout=30, chunk_size=8192):
    """
    Download a PDF file from a URL and save it to a specified path.

    Args:
        url (str): The URL of the PDF file to download
        save_path (str): The directory path where the PDF should be saved
        filename (str, optional): Custom filename for the PDF. If None, extracts from URL
        timeout (int): Request timeout in seconds (default: 30)
        chunk_size (int): Size of chunks to download at a time (default: 8192 bytes)

    Returns:
        str: Full path of the downloaded file if successful

    Raises:
        ValueError: If URL is invalid or save_path doesn't exist
        requests.RequestException: If download fails
        IOError: If file cannot be written
    """

    # Validate URL
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL format")

    # Create save directory if it doesn't exist
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Determine filename
    if filename is None:
        # Extract filename from URL
        url_path = parsed_url.path
        filename = os.path.basename(url_path)

        # If no filename in URL, create a default one
        if not filename or not filename.endswith('.pdf'):
            filename = 'downloaded_file.pdf'

    # Ensure filename has .pdf extension
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'

    # Full file path
    file_path = save_dir / filename

    try:
        # Send GET request with stream=True for large files
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Check if the content is actually a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
            # Try to guess from content
            first_chunk = response.iter_content(chunk_size=1024).__next__()
            if not first_chunk.startswith(b'%PDF'):
                print(f"Warning: Content may not be a PDF file (Content-Type: {content_type})")

        # Download and save the file
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filter out keep-alive chunks
                    file.write(chunk)
                    downloaded_size += len(chunk)

                    # Optional: Print progress for large files
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\rDownloading: {progress:.1f}%", end='', flush=True)

        if total_size > 0:
            print()  # New line after progress

        print(f"PDF downloaded successfully: {file_path}")
        return str(file_path)

    except requests.exceptions.Timeout:
        raise requests.RequestException(f"Download timed out after {timeout} seconds")
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to download PDF: {str(e)}")
    except IOError as e:
        raise IOError(f"Failed to save file: {str(e)}")
