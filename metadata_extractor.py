"""Enhanced metadata extraction for images, PDFs, and documents"""

import json
import logging
import mimetypes
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, List, Any
from PIL import Image
from PIL.ExifTags import TAGS as EXIF_TAGS
import PyPDF2

logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class GPSCoordinate:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def geohash(self) -> str:
        """Generate a basic geohash for proximity clustering"""
        # Simplified geohash for proximity (5 decimal places ≈ 1.1m precision)
        lat_rounded = round(self.latitude, 5)
        lon_rounded = round(self.longitude, 5)
        return f"{lat_rounded},{lon_rounded}"


@dataclass
class ImageMetadata:
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    gps: Optional[GPSCoordinate] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    date_taken: Optional[str] = None
    orientation: Optional[int] = None
    exif_data: Optional[Dict[str, Any]] = None
    hash_md5: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['gps'] = self.gps.to_dict() if self.gps else None
        return d


@dataclass
class PDFMetadata:
    file_path: str
    file_name: str
    file_size: int
    pages: int
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    keywords: Optional[List[str]] = None
    text_preview: Optional[str] = None
    hash_md5: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetadataExtractor:
    """Extract metadata from various file types"""

    @staticmethod
    def convert_gps_to_decimal(gps_data: tuple) -> float:
        """Convert GPS coordinate tuple (degrees, minutes, seconds) to decimal"""
        degrees = gps_data[0]
        minutes = gps_data[1] / 60.0
        seconds = gps_data[2] / 3600.0
        return degrees + minutes + seconds

    @staticmethod
    def extract_gps_from_exif(exif_dict: Dict[int, Any]) -> Optional[GPSCoordinate]:
        """Extract GPS coordinates from EXIF data"""
        try:
            gps_ifd = exif_dict.get(34853)  # GPSInfo tag
            if not gps_ifd:
                return None

            gps_data = {}
            for key, val in gps_ifd.items():
                tag_name = EXIF_TAGS.get(key, key)
                gps_data[tag_name] = val

            lat = gps_data.get('GPSLatitude')
            lon = gps_data.get('GPSLongitude')
            lat_ref = gps_data.get('GPSLatitudeRef', 'N')
            lon_ref = gps_data.get('GPSLongitudeRef', 'E')
            alt = gps_data.get('GPSAltitude')
            timestamp = gps_data.get('GPSTimeStamp')

            if not lat or not lon:
                return None

            lat_decimal = MetadataExtractor.convert_gps_to_decimal(lat)
            lon_decimal = MetadataExtractor.convert_gps_to_decimal(lon)

            if lat_ref == 'S':
                lat_decimal = -lat_decimal
            if lon_ref == 'W':
                lon_decimal = -lon_decimal

            altitude = None
            if alt:
                altitude = float(alt[0]) / float(alt[1]) if alt[1] != 0 else 0

            return GPSCoordinate(
                latitude=lat_decimal,
                longitude=lon_decimal,
                altitude=altitude,
                timestamp=str(timestamp) if timestamp else None
            )
        except Exception as e:
            logging.warning(f"Failed to extract GPS from EXIF: {e}")
            return None

    @staticmethod
    def extract_image_metadata(file_path: str) -> Optional[ImageMetadata]:
        """Extract metadata from image file"""
        try:
            path = Path(file_path)
            if not path.exists():
                logging.warning(f"Image file not found: {file_path}")
                return None

            img = Image.open(file_path)
            width, height = img.size
            mime_type = mimetypes.guess_type(file_path)[0] or "image/unknown"

            exif_dict = {}
            exif_readable = {}
            gps = None
            camera_make = None
            camera_model = None
            date_taken = None
            orientation = None

            try:
                exif_dict = img._getexif() or {}
                for tag_id, value in exif_dict.items():
                    tag_name = EXIF_TAGS.get(tag_id, tag_id)
                    exif_readable[tag_name] = str(value)[:200]  # Truncate for storage

                # Extract specific fields
                gps = MetadataExtractor.extract_gps_from_exif(exif_dict)
                camera_make = exif_readable.get('Make')
                camera_model = exif_readable.get('Model')
                date_taken = exif_readable.get('DateTime')
                orientation = exif_dict.get(274)  # Orientation tag
            except Exception as e:
                logging.debug(f"Could not extract full EXIF from {file_path}: {e}")

            import hashlib
            file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

            return ImageMetadata(
                file_path=str(path.absolute()),
                file_name=path.name,
                file_size=path.stat().st_size,
                mime_type=mime_type,
                width=width,
                height=height,
                gps=gps,
                camera_make=camera_make,
                camera_model=camera_model,
                date_taken=date_taken,
                orientation=orientation,
                exif_data=exif_readable if exif_readable else None,
                hash_md5=file_hash
            )
        except Exception as e:
            logging.error(f"Failed to extract image metadata from {file_path}: {e}")
            return None

    @staticmethod
    def extract_pdf_metadata(file_path: str) -> Optional[PDFMetadata]:
        """Extract metadata from PDF file"""
        try:
            path = Path(file_path)
            if not path.exists():
                logging.warning(f"PDF file not found: {file_path}")
                return None

            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                pages = len(pdf_reader.pages)
                metadata = pdf_reader.metadata or {}

                text_preview = ""
                if pages > 0:
                    text_preview = pdf_reader.pages[0].extract_text()[:500]

            import hashlib
            file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

            return PDFMetadata(
                file_path=str(path.absolute()),
                file_name=path.name,
                file_size=path.stat().st_size,
                pages=pages,
                title=metadata.get('/Title', '').decode() if isinstance(metadata.get('/Title'), bytes) else metadata.get('/Title'),
                author=metadata.get('/Author', '').decode() if isinstance(metadata.get('/Author'), bytes) else metadata.get('/Author'),
                subject=metadata.get('/Subject', '').decode() if isinstance(metadata.get('/Subject'), bytes) else metadata.get('/Subject'),
                creation_date=str(metadata.get('/CreationDate')),
                modification_date=str(metadata.get('/ModDate')),
                keywords=[kw.strip() for kw in (metadata.get('/Keywords', '') or '').split(',')],
                text_preview=text_preview,
                hash_md5=file_hash
            )
        except Exception as e:
            logging.error(f"Failed to extract PDF metadata from {file_path}: {e}")
            return None

    @staticmethod
    def extract_file_metadata(file_path: str) -> Optional[Dict[str, Any]]:
        """Auto-detect file type and extract appropriate metadata"""
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type and mime_type.startswith('image/'):
            return asdict(MetadataExtractor.extract_image_metadata(file_path) or {})
        elif mime_type == 'application/pdf':
            return asdict(MetadataExtractor.extract_pdf_metadata(file_path) or {})
        else:
            logging.warning(f"Unsupported file type for metadata extraction: {mime_type}")
            return None
